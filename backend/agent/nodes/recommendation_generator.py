"""建议生成 Node — 基于分析结果生成行动建议"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.recommendation_generator import RECOMMENDATION_GENERATOR_SYSTEM_PROMPT, RECOMMENDATION_GENERATOR_USER_PROMPT
from agent.llm import get_llm


def recommendation_generator_node(state: AgentState) -> dict:
    """基于数据分析结果生成可执行的行动建议"""

    user_message = state.get("user_message", "")
    analysis_result = state.get("analysis_result", {})
    key_insights = state.get("key_insights", [])
    anomalies = state.get("anomalies", [])
    trend_analysis = state.get("trend_analysis", {})

    step = {
        "node_name": "recommendation_generator",
        "status": NodeStatus.RUNNING.value,
        "title": "建议生成",
        "detail": "正在生成行动建议...",
        "data": {},
    }

    llm = get_llm()
    prompt = RECOMMENDATION_GENERATOR_USER_PROMPT.format(
        user_message=user_message,
        analysis_result=json.dumps(analysis_result, ensure_ascii=False),
        key_insights=json.dumps(key_insights, ensure_ascii=False),
        anomalies=json.dumps(anomalies, ensure_ascii=False),
        trend_analysis=json.dumps(trend_analysis, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": RECOMMENDATION_GENERATOR_SYSTEM_PROMPT},
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
            "recommendations": [],
            "priority_actions": [],
            "risk_mitigations": [],
            "next_steps": [],
        }

    recommendations = result.get("recommendations", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"生成了 {len(recommendations)} 条建议"
    step["data"] = {
        "recommendation_count": len(recommendations),
        "priority_action_count": len(result.get("priority_actions", [])),
        "risk_mitigation_count": len(result.get("risk_mitigations", [])),
    }

    return {
        "recommendations": recommendations,
        "priority_actions": result.get("priority_actions", []),
        "risk_mitigations": result.get("risk_mitigations", []),
        "next_steps": result.get("next_steps", []),
        "steps": [step],
    }
