"""图表推荐 Node — 根据数据特征推荐最佳图表类型"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.chart_recommender import CHART_RECOMMENDER_SYSTEM_PROMPT, CHART_RECOMMENDER_USER_PROMPT
from agent.llm import get_llm


def chart_recommender_node(state: AgentState) -> dict:
    """根据数据特征和用户意图推荐最佳的可视化图表类型"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    analysis_result = state.get("analysis_result", {})
    query_type = state.get("query_type", "unknown")

    step = {
        "node_name": "chart_recommender",
        "status": NodeStatus.RUNNING.value,
        "title": "图表推荐",
        "detail": "正在推荐最佳图表类型...",
        "data": {},
    }

    data_preview = sql_result[:20]
    
    llm = get_llm()
    prompt = CHART_RECOMMENDER_USER_PROMPT.format(
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data_sample=json.dumps(data_preview, ensure_ascii=False, indent=2),
        row_count=len(sql_result),
        analysis_summary=json.dumps(analysis_result.get("summary", ""), ensure_ascii=False),
        query_type=query_type,
    )

    response = llm.invoke([
        {"role": "system", "content": CHART_RECOMMENDER_SYSTEM_PROMPT},
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
            "recommended_chart": "table",
            "chart_alternatives": [],
            "chart_reason": "默认使用表格展示",
            "visualization_config": {},
        }

    recommended_chart = result.get("recommended_chart", "table")
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"推荐图表类型: {recommended_chart}"
    step["data"] = {
        "recommended_chart": recommended_chart,
        "alternatives": result.get("chart_alternatives", []),
        "reason": result.get("chart_reason", ""),
    }

    return {
        "recommended_chart": recommended_chart,
        "chart_alternatives": result.get("chart_alternatives", []),
        "chart_reason": result.get("chart_reason", ""),
        "visualization_config": result.get("visualization_config", {}),
        "steps": [step],
    }
