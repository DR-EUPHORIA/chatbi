"""异常检测 Node — 检测数据中的异常值和异常模式"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.anomaly_detector import ANOMALY_DETECTOR_SYSTEM_PROMPT, ANOMALY_DETECTOR_USER_PROMPT
from agent.llm import get_llm


def anomaly_detector_node(state: AgentState) -> dict:
    """检测数据中的异常值、离群点和异常模式"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    analysis_result = state.get("analysis_result", {})

    step = {
        "node_name": "anomaly_detector",
        "status": NodeStatus.RUNNING.value,
        "title": "异常检测",
        "detail": "正在检测数据异常...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = ANOMALY_DETECTOR_USER_PROMPT.format(
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        analysis_context=json.dumps(analysis_result, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": ANOMALY_DETECTOR_SYSTEM_PROMPT},
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
            "anomalies": [],
            "outliers": [],
            "anomaly_score": 0.0,
            "anomaly_insights": [],
        }

    anomalies = result.get("anomalies", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"检测到 {len(anomalies)} 个异常"
    step["data"] = {
        "anomaly_count": len(anomalies),
        "outlier_count": len(result.get("outliers", [])),
        "anomaly_score": result.get("anomaly_score", 0.0),
    }

    return {
        "anomalies": anomalies,
        "outliers": result.get("outliers", []),
        "anomaly_score": result.get("anomaly_score", 0.0),
        "anomaly_insights": result.get("anomaly_insights", []),
        "steps": [step],
    }
