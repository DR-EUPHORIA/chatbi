"""SQL 生成 Node — 根据用户问题和 Schema 生成 SQL"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.sql_generator import SQL_GENERATOR_SYSTEM_PROMPT, SQL_GENERATOR_USER_PROMPT
from agent.llm import get_llm
from knowledge.semantic_layer import get_glossary_text
from knowledge.few_shot import get_similar_examples


def _extract_json_from_text(text: str) -> dict | None:
    """尝试从 LLM 输出文本中提取 JSON 对象"""
    json_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass
    json_match = re.search(r'\{[^{}]*"sql"[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def sql_generator_node(state: AgentState) -> dict:
    """根据用户的自然语言问题生成 SQL 查询语句"""

    user_message = state.get("user_message", "")
    dataset_id = state.get("dataset_id")
    schema_context = state.get("schema_context", "")

    step = {
        "node_name": "sql_generator",
        "status": NodeStatus.RUNNING.value,
        "title": "生成 SQL",
        "detail": "正在根据您的问题生成查询语句...",
        "data": {},
    }

    glossary = get_glossary_text(dataset_id)
    few_shot = get_similar_examples(user_message, dataset_id)

    system_prompt = SQL_GENERATOR_SYSTEM_PROMPT.format(
        glossary=glossary if glossary else "暂无业务术语映射",
        few_shot_examples=few_shot if few_shot else "暂无历史示例",
    )

    user_prompt = SQL_GENERATOR_USER_PROMPT.format(
        user_message=user_message,
        dialect="sqlite",
        schema_context=schema_context,
    )

    llm = get_llm()
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ])

    generated_sql = ""
    sql_explanation = ""
    result = {}

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        extracted = _extract_json_from_text(response.content)
        if extracted:
            result = extracted
        else:
            content = response.content
            if "SELECT" in content.upper():
                sql_start = content.upper().find("SELECT")
                generated_sql = content[sql_start:].strip()
                generated_sql = generated_sql.replace("```", "").strip()
                generated_sql = generated_sql.rstrip(";") + ";"
                sql_explanation = "从 LLM 输出中提取的 SQL"
            else:
                step["status"] = NodeStatus.FAILED.value
                step["detail"] = "SQL 生成失败：无法解析 LLM 输出"
                return {"error": "SQL 生成失败", "steps": [step]}

    if not generated_sql:
        generated_sql = result.get("sql", "")
        sql_explanation = result.get("explanation", "")

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"SQL 已生成：{generated_sql[:80]}..."
    step["data"] = {
        "sql": generated_sql,
        "explanation": sql_explanation,
        "tables_used": result.get("tables_used", []),
    }

    return {
        "generated_sql": generated_sql,
        "sql_explanation": sql_explanation,
        "steps": [step],
    }
