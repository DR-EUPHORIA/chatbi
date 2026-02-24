"""洞察提取 Node — 从分析结果中提取关键洞察"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.insight_extractor import INSIGHT_EXTRACTOR_SYSTEM_PROMPT, INSIGHT_EXTRACTOR_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def insight_extractor_node(state: AgentState) -> dict:
    """从各种分析结果中提取和整合关键业务洞察"""

    user_message = state.get("user_message", "")
    analysis_result = state.get("analysis_result", {})
    trend_analysis = state.get("trend_analysis", {})
    comparison_analysis = state.get("comparison_analysis", {})
    anomalies = state.get("anomalies", [])

    step = {
        "node_name": "insight_extractor",
        "status": NodeStatus.RUNNING.value,
        "title": "洞察提取",
        "detail": "正在提取关键洞察...",
        "data": {},
    }

    llm = get_llm()
    prompt = safe_format_prompt(INSIGHT_EXTRACTOR_USER_PROMPT, 
        user_message=user_message,
        analysis_result=json.dumps(analysis_result, ensure_ascii=False),
        trend_analysis=json.dumps(trend_analysis, ensure_ascii=False),
        comparison_analysis=json.dumps(comparison_analysis, ensure_ascii=False),
        anomalies=json.dumps(anomalies, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": INSIGHT_EXTRACTOR_SYSTEM_PROMPT},
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
            "key_insights": [],
            "insight_priority": [],
            "action_items": [],
            "follow_up_questions": [],
        }

    key_insights = result.get("key_insights", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"提取了 {len(key_insights)} 个关键洞察"
    step["data"] = {
        "insight_count": len(key_insights),
        "action_item_count": len(result.get("action_items", [])),
        "follow_up_count": len(result.get("follow_up_questions", [])),
    }

    return {
        "key_insights": key_insights,
        "insight_priority": result.get("insight_priority", []),
        "action_items": result.get("action_items", []),
        "follow_up_questions": result.get("follow_up_questions", []),
        "steps": [step],
    }
