"""趋势分析 Node — 分析数据的时间趋势"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.trend_analyzer import TREND_ANALYZER_SYSTEM_PROMPT, TREND_ANALYZER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def trend_analyzer_node(state: AgentState) -> dict:
    """分析数据的时间趋势，识别增长、下降、周期性等模式"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    time_entities = state.get("time_entities", [])

    step = {
        "node_name": "trend_analyzer",
        "status": NodeStatus.RUNNING.value,
        "title": "趋势分析",
        "detail": "正在分析数据趋势...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = safe_format_prompt(TREND_ANALYZER_USER_PROMPT, 
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        time_entities=json.dumps(time_entities, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": TREND_ANALYZER_SYSTEM_PROMPT},
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
            "trend_direction": "stable",
            "trend_strength": 0.5,
            "seasonality": None,
            "turning_points": [],
            "trend_insights": [],
        }

    step["status"] = NodeStatus.SUCCESS.value
    trend_direction = result.get("trend_direction", "stable")
    step["detail"] = f"趋势方向: {trend_direction}"
    step["data"] = {
        "trend_direction": trend_direction,
        "trend_strength": result.get("trend_strength", 0.5),
        "has_seasonality": result.get("seasonality") is not None,
    }

    return {
        "trend_analysis": result,
        "trend_direction": trend_direction,
        "trend_strength": result.get("trend_strength", 0.5),
        "seasonality": result.get("seasonality"),
        "turning_points": result.get("turning_points", []),
        "trend_insights": result.get("trend_insights", []),
        "steps": [step],
    }
