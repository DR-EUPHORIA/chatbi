"""SQL 验证 Node — 验证生成的 SQL 语法和语义正确性"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.sql_validator import SQL_VALIDATOR_SYSTEM_PROMPT, SQL_VALIDATOR_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def sql_validator_node(state: AgentState) -> dict:
    """验证生成的 SQL 是否语法正确、语义合理"""

    generated_sql = state.get("generated_sql", "")
    matched_tables = state.get("matched_tables", [])
    schema_context = state.get("schema_context", "")

    step = {
        "node_name": "sql_validator",
        "status": NodeStatus.RUNNING.value,
        "title": "SQL 验证",
        "detail": "正在验证 SQL 语句...",
        "data": {},
    }

    schema_text = schema_context if schema_context else json.dumps(matched_tables, ensure_ascii=False)
    if not schema_text:
        schema_text = "暂无表结构信息"

    llm = get_llm()
    prompt = safe_format_prompt(SQL_VALIDATOR_USER_PROMPT, 
        sql=generated_sql,
        schema_context=schema_text,
        dialect="sqlite",
        # 兼容历史 Prompt 占位符命名
        generated_sql=generated_sql,
        matched_tables=schema_text,
    )

    response = llm.invoke([
        {"role": "system", "content": SQL_VALIDATOR_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response.content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                result = {}
        else:
            result = {}

    if not isinstance(result, dict):
        result = {
            "is_valid": True,
            "syntax_errors": [],
            "semantic_warnings": [],
            "suggestions": [],
        }

    is_valid = result.get("is_valid", True)
    syntax_errors = result.get("syntax_errors")
    semantic_warnings = result.get("semantic_warnings")
    suggestions = result.get("suggestions")

    # 兼容 Prompt 示例输出：issues / warnings
    if syntax_errors is None and isinstance(result.get("issues"), list):
        syntax_errors = []
        for issue in result.get("issues", []):
            if isinstance(issue, dict):
                syntax_errors.append(issue.get("message", str(issue)))
            else:
                syntax_errors.append(str(issue))
    if semantic_warnings is None:
        semantic_warnings = result.get("warnings", [])
    if suggestions is None:
        suggestions = []

    if not isinstance(syntax_errors, list):
        syntax_errors = []
    if not isinstance(semantic_warnings, list):
        semantic_warnings = []
    if not isinstance(suggestions, list):
        suggestions = []

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = "SQL 验证通过" if is_valid else f"发现 {len(syntax_errors)} 个问题"
    step["data"] = {
        "is_valid": is_valid,
        "error_count": len(syntax_errors),
        "warning_count": len(semantic_warnings),
    }

    return {
        "sql_is_valid": is_valid,
        "sql_syntax_errors": syntax_errors,
        "sql_semantic_warnings": semantic_warnings,
        "sql_suggestions": suggestions,
        "steps": [step],
    }
