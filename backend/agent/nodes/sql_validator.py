"""SQL 验证 Node — 验证生成的 SQL 语法和语义正确性"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.sql_validator import SQL_VALIDATOR_SYSTEM_PROMPT, SQL_VALIDATOR_USER_PROMPT
from agent.llm import get_llm


def sql_validator_node(state: AgentState) -> dict:
    """验证生成的 SQL 是否语法正确、语义合理"""

    generated_sql = state.get("generated_sql", "")
    matched_tables = state.get("matched_tables", [])
    user_message = state.get("user_message", "")

    step = {
        "node_name": "sql_validator",
        "status": NodeStatus.RUNNING.value,
        "title": "SQL 验证",
        "detail": "正在验证 SQL 语句...",
        "data": {},
    }

    llm = get_llm()
    prompt = SQL_VALIDATOR_USER_PROMPT.format(
        generated_sql=generated_sql,
        matched_tables=json.dumps(matched_tables, ensure_ascii=False),
        user_message=user_message,
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

    step["status"] = NodeStatus.SUCCESS.value
    is_valid = result.get("is_valid", True)
    step["detail"] = "SQL 验证通过" if is_valid else f"发现 {len(result.get('syntax_errors', []))} 个问题"
    step["data"] = {
        "is_valid": is_valid,
        "error_count": len(result.get("syntax_errors", [])),
        "warning_count": len(result.get("semantic_warnings", [])),
    }

    return {
        "sql_is_valid": is_valid,
        "sql_syntax_errors": result.get("syntax_errors", []),
        "sql_semantic_warnings": result.get("semantic_warnings", []),
        "sql_suggestions": result.get("suggestions", []),
        "steps": [step],
    }
