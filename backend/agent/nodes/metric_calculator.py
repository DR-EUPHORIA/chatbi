"""指标计算 Node — 计算各种业务指标"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.metric_calculator import METRIC_CALCULATOR_SYSTEM_PROMPT, METRIC_CALCULATOR_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def metric_calculator_node(state: AgentState) -> dict:
    """计算各种业务指标，如同比、环比、占比、增长率等"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    metric_entities = state.get("metric_entities", [])

    step = {
        "node_name": "metric_calculator",
        "status": NodeStatus.RUNNING.value,
        "title": "指标计算",
        "detail": "正在计算业务指标...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = safe_format_prompt(METRIC_CALCULATOR_USER_PROMPT, 
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        metric_entities=json.dumps(metric_entities, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": METRIC_CALCULATOR_SYSTEM_PROMPT},
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
            "calculated_metrics": {},
            "metric_definitions": [],
            "metric_insights": [],
        }

    calculated_metrics = result.get("calculated_metrics", {})
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"计算了 {len(calculated_metrics)} 个指标"
    step["data"] = {
        "metric_count": len(calculated_metrics),
        "metrics": list(calculated_metrics.keys()),
    }

    return {
        "calculated_metrics": calculated_metrics,
        "metric_definitions": result.get("metric_definitions", []),
        "metric_insights": result.get("metric_insights", []),
        "steps": [step],
    }
