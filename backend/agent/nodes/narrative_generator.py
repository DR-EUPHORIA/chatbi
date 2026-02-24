"""叙事生成 Node — 生成数据故事"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.narrative_generator import NARRATIVE_GENERATOR_SYSTEM_PROMPT, NARRATIVE_GENERATOR_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def narrative_generator_node(state: AgentState) -> dict:
    """将数据分析结果转化为引人入胜的数据故事"""

    user_message = state.get("user_message", "")
    analysis_result = state.get("analysis_result", {})
    key_insights = state.get("key_insights", [])
    trend_analysis = state.get("trend_analysis", {})
    recommendations = state.get("recommendations", [])

    step = {
        "node_name": "narrative_generator",
        "status": NodeStatus.RUNNING.value,
        "title": "叙事生成",
        "detail": "正在生成数据故事...",
        "data": {},
    }

    llm = get_llm()
    prompt = safe_format_prompt(NARRATIVE_GENERATOR_USER_PROMPT, 
        user_message=user_message,
        analysis_result=json.dumps(analysis_result, ensure_ascii=False),
        insights=json.dumps(key_insights, ensure_ascii=False),
        audience="business_user",
        tone="professional_optimistic",
    )

    response = llm.invoke([
        {"role": "system", "content": NARRATIVE_GENERATOR_SYSTEM_PROMPT},
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
            "narrative_type": "summary",
            "title": "",
            "hook": "",
            "sections": [],
            "key_quotes": [],
            "summary": "",
        }

    sections = result.get("sections", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"生成了包含 {len(sections)} 个章节的数据故事"
    step["data"] = {
        "narrative_type": result.get("narrative_type", "summary"),
        "section_count": len(sections),
        "title": result.get("title", ""),
    }

    return {
        "narrative": result,
        "narrative_type": result.get("narrative_type", "summary"),
        "narrative_title": result.get("title", ""),
        "narrative_sections": sections,
        "narrative_summary": result.get("summary", ""),
        "steps": [step],
    }
