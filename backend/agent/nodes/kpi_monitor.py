"""KPI 监控 Node — 监控关键业务指标"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.kpi_monitor import KPI_MONITOR_SYSTEM_PROMPT, KPI_MONITOR_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def kpi_monitor_node(state: AgentState) -> dict:
    """监控关键业务指标，检测是否达标、是否有异常"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    calculated_metrics = state.get("calculated_metrics", {})

    step = {
        "node_name": "kpi_monitor",
        "status": NodeStatus.RUNNING.value,
        "title": "KPI 监控",
        "detail": "正在监控 KPI 指标...",
        "data": {},
    }

    data_preview = sql_result[:50]
    
    llm = get_llm()
    prompt = safe_format_prompt(KPI_MONITOR_USER_PROMPT, 
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        calculated_metrics=json.dumps(calculated_metrics, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": KPI_MONITOR_SYSTEM_PROMPT},
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
            "kpi_status": [],
            "alerts": [],
            "health_score": 0.8,
            "kpi_insights": [],
        }

    kpi_status = result.get("kpi_status", [])
    alerts = result.get("alerts", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"监控了 {len(kpi_status)} 个 KPI，{len(alerts)} 个告警"
    step["data"] = {
        "kpi_count": len(kpi_status),
        "alert_count": len(alerts),
        "health_score": result.get("health_score", 0.8),
    }

    return {
        "kpi_status": kpi_status,
        "kpi_alerts": alerts,
        "kpi_health_score": result.get("health_score", 0.8),
        "kpi_insights": result.get("kpi_insights", []),
        "steps": [step],
    }
