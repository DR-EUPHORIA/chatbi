"""摘要生成 Node — 生成数据分析的简洁摘要"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.summary_generator import SUMMARY_GENERATOR_SYSTEM_PROMPT, SUMMARY_GENERATOR_USER_PROMPT
from agent.llm import get_llm


def summary_generator_node(state: AgentState) -> dict:
    """生成数据分析结果的简洁、易懂的摘要"""

    user_message = state.get("user_message", "")
    analysis_result = state.get("analysis_result", {})
    key_insights = state.get("key_insights", [])
    trend_analysis = state.get("trend_analysis", {})

    step = {
        "node_name": "summary_generator",
        "status": NodeStatus.RUNNING.value,
        "title": "摘要生成",
        "detail": "正在生成分析摘要...",
        "data": {},
    }

    llm = get_llm()
    prompt = SUMMARY_GENERATOR_USER_PROMPT.format(
        user_message=user_message,
        analysis_result=json.dumps(analysis_result, ensure_ascii=False),
        key_insights=json.dumps(key_insights, ensure_ascii=False),
        trend_analysis=json.dumps(trend_analysis, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": SUMMARY_GENERATOR_SYSTEM_PROMPT},
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
            "executive_summary": "",
            "key_points": [],
            "conclusion": "",
            "word_count": 0,
        }

    executive_summary = result.get("executive_summary", "")
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"生成了 {len(executive_summary)} 字的摘要"
    step["data"] = {
        "summary_length": len(executive_summary),
        "key_point_count": len(result.get("key_points", [])),
    }

    return {
        "executive_summary": executive_summary,
        "summary_key_points": result.get("key_points", []),
        "summary_conclusion": result.get("conclusion", ""),
        "steps": [step],
    }
