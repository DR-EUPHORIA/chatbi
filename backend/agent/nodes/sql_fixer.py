"""SQL 修正 Node — 根据错误信息修正 SQL"""

import json
from agent.state import AgentState, NodeStatus
from agent.prompts.sql_fixer import SQL_FIXER_SYSTEM_PROMPT, SQL_FIXER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def sql_fixer_node(state: AgentState) -> dict:
    """根据 SQL 执行错误信息修正 SQL"""

    generated_sql = state.get("generated_sql", "")
    sql_error = state.get("sql_error", "")
    schema_context = state.get("schema_context", "")
    retry_count = state.get("sql_retry_count", 0)
    next_retry_count = retry_count + 1

    step = {
        "node_name": "sql_fixer",
        "status": NodeStatus.RUNNING.value,
        "title": "修正 SQL",
        "detail": f"正在修正 SQL（第 {retry_count} 次重试）...",
        "data": {},
    }

    llm = get_llm()
    prompt = safe_format_prompt(SQL_FIXER_USER_PROMPT, 
        original_sql=generated_sql,
        error=sql_error,
        schema_context=schema_context,
        dialect="sqlite",
    )

    response = llm.invoke([
        {"role": "system", "content": SQL_FIXER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    fixed_sql = generated_sql

    try:
        result = json.loads(response.content)
        fixed_sql = result.get("fixed_sql", generated_sql)
        fix_explanation = result.get("fix_explanation", "")

        step["status"] = NodeStatus.SUCCESS.value
        step["detail"] = f"SQL 已修正：{fix_explanation}"
        step["data"] = {"fixed_sql": fixed_sql, "fix_explanation": fix_explanation}

    except json.JSONDecodeError:
        content = response.content
        if "SELECT" in content.upper():
            sql_start = content.upper().find("SELECT")
            fixed_sql = content[sql_start:].strip()
            fixed_sql = fixed_sql.replace("```", "").strip()
            fixed_sql = fixed_sql.rstrip(";") + ";"
            step["status"] = NodeStatus.SUCCESS.value
            step["detail"] = "SQL 已修正（从文本中提取）"
        else:
            step["status"] = NodeStatus.FAILED.value
            step["detail"] = "SQL 修正失败"

    return {
        "generated_sql": fixed_sql,
        "sql_retry_count": next_retry_count,
        "steps": [step],
    }
