"""预测生成 Node — 基于历史数据生成预测"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.forecast_generator import FORECAST_GENERATOR_SYSTEM_PROMPT, FORECAST_GENERATOR_USER_PROMPT
from agent.llm import get_llm


def forecast_generator_node(state: AgentState) -> dict:
    """基于历史数据和趋势分析生成未来预测"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    trend_analysis = state.get("trend_analysis", {})
    time_entities = state.get("time_entities", [])

    step = {
        "node_name": "forecast_generator",
        "status": NodeStatus.RUNNING.value,
        "title": "预测生成",
        "detail": "正在生成数据预测...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = FORECAST_GENERATOR_USER_PROMPT.format(
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        trend_analysis=json.dumps(trend_analysis, ensure_ascii=False),
        time_entities=json.dumps(time_entities, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": FORECAST_GENERATOR_SYSTEM_PROMPT},
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
            "forecasts": [],
            "forecast_method": "unknown",
            "confidence_interval": {},
            "forecast_insights": [],
            "assumptions": [],
        }

    forecasts = result.get("forecasts", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"生成了 {len(forecasts)} 个预测点"
    step["data"] = {
        "forecast_count": len(forecasts),
        "forecast_method": result.get("forecast_method", "unknown"),
    }

    return {
        "forecasts": forecasts,
        "forecast_method": result.get("forecast_method", "unknown"),
        "confidence_interval": result.get("confidence_interval", {}),
        "forecast_insights": result.get("forecast_insights", []),
        "forecast_assumptions": result.get("assumptions", []),
        "steps": [step],
    }
