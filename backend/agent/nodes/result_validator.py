"""结果验证 Node — 验证 SQL 执行结果的合理性"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.result_validator import RESULT_VALIDATOR_SYSTEM_PROMPT, RESULT_VALIDATOR_USER_PROMPT
from agent.llm import get_llm


def result_validator_node(state: AgentState) -> dict:
    """验证 SQL 执行结果是否合理、是否符合用户预期"""

    user_message = state.get("user_message", "")
    generated_sql = state.get("generated_sql", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])

    step = {
        "node_name": "result_validator",
        "status": NodeStatus.RUNNING.value,
        "title": "结果验证",
        "detail": "正在验证查询结果...",
        "data": {},
    }

    data_preview = sql_result[:20]
    
    llm = get_llm()
    prompt = RESULT_VALIDATOR_USER_PROMPT.format(
        user_message=user_message,
        generated_sql=generated_sql,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        row_count=len(sql_result),
    )

    response = llm.invoke([
        {"role": "system", "content": RESULT_VALIDATOR_SYSTEM_PROMPT},
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
            "validation_issues": [],
            "data_quality_score": 0.8,
            "recommendations": [],
        }

    step["status"] = NodeStatus.SUCCESS.value
    is_valid = result.get("is_valid", True)
    step["detail"] = "结果验证通过" if is_valid else f"发现 {len(result.get('validation_issues', []))} 个问题"
    step["data"] = {
        "is_valid": is_valid,
        "data_quality_score": result.get("data_quality_score", 0.8),
        "issue_count": len(result.get("validation_issues", [])),
    }

    return {
        "result_is_valid": is_valid,
        "result_validation_issues": result.get("validation_issues", []),
        "data_quality_score": result.get("data_quality_score", 0.8),
        "result_recommendations": result.get("recommendations", []),
        "steps": [step],
    }
