"""对比分析 Node — 进行多维度数据对比分析"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.comparison_analyzer import COMPARISON_ANALYZER_SYSTEM_PROMPT, COMPARISON_ANALYZER_USER_PROMPT
from agent.llm import get_llm


def comparison_analyzer_node(state: AgentState) -> dict:
    """进行多维度数据对比分析，包括同比、环比、分组对比等"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    dimension_entities = state.get("dimension_entities", [])

    step = {
        "node_name": "comparison_analyzer",
        "status": NodeStatus.RUNNING.value,
        "title": "对比分析",
        "detail": "正在进行数据对比分析...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = COMPARISON_ANALYZER_USER_PROMPT.format(
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        dimensions=json.dumps(dimension_entities, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": COMPARISON_ANALYZER_SYSTEM_PROMPT},
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
            "comparison_type": "unknown",
            "comparisons": [],
            "rankings": [],
            "comparison_insights": [],
        }

    comparisons = result.get("comparisons", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"完成 {len(comparisons)} 项对比分析"
    step["data"] = {
        "comparison_type": result.get("comparison_type", "unknown"),
        "comparison_count": len(comparisons),
        "ranking_count": len(result.get("rankings", [])),
    }

    return {
        "comparison_analysis": result,
        "comparison_type": result.get("comparison_type", "unknown"),
        "comparisons": comparisons,
        "rankings": result.get("rankings", []),
        "comparison_insights": result.get("comparison_insights", []),
        "steps": [step],
    }
