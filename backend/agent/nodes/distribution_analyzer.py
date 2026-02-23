"""分布分析 Node — 分析数据的分布特征"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.distribution_analyzer import DISTRIBUTION_ANALYZER_SYSTEM_PROMPT, DISTRIBUTION_ANALYZER_USER_PROMPT
from agent.llm import get_llm


def distribution_analyzer_node(state: AgentState) -> dict:
    """分析数据的分布特征，包括集中趋势、离散程度、分布形态等"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    metric_columns = state.get("metric_columns", [])

    step = {
        "node_name": "distribution_analyzer",
        "status": NodeStatus.RUNNING.value,
        "title": "分布分析",
        "detail": "正在分析数据分布...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = DISTRIBUTION_ANALYZER_USER_PROMPT.format(
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        metric_columns=json.dumps(metric_columns, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": DISTRIBUTION_ANALYZER_SYSTEM_PROMPT},
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
            "distribution_stats": {},
            "distribution_type": "unknown",
            "skewness": 0,
            "kurtosis": 0,
            "distribution_insights": [],
        }

    distribution_stats = result.get("distribution_stats", {})
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"分布类型: {result.get('distribution_type', 'unknown')}"
    step["data"] = {
        "distribution_type": result.get("distribution_type", "unknown"),
        "analyzed_columns": len(distribution_stats),
    }

    return {
        "distribution_stats": distribution_stats,
        "distribution_type": result.get("distribution_type", "unknown"),
        "skewness": result.get("skewness", 0),
        "kurtosis": result.get("kurtosis", 0),
        "distribution_insights": result.get("distribution_insights", []),
        "steps": [step],
    }
