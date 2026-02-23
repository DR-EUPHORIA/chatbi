"""归因分析 Node — 分析指标变化的原因"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.attribution_analyzer import ATTRIBUTION_ANALYZER_SYSTEM_PROMPT, ATTRIBUTION_ANALYZER_USER_PROMPT
from agent.llm import get_llm


def attribution_analyzer_node(state: AgentState) -> dict:
    """分析指标变化的归因，找出影响因素和贡献度"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    analysis_result = state.get("analysis_result", {})
    comparison_analysis = state.get("comparison_analysis", {})

    step = {
        "node_name": "attribution_analyzer",
        "status": NodeStatus.RUNNING.value,
        "title": "归因分析",
        "detail": "正在分析变化归因...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = ATTRIBUTION_ANALYZER_USER_PROMPT.format(
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        analysis_result=json.dumps(analysis_result, ensure_ascii=False),
        comparison_analysis=json.dumps(comparison_analysis, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": ATTRIBUTION_ANALYZER_SYSTEM_PROMPT},
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
            "attributions": [],
            "top_contributors": [],
            "contribution_breakdown": {},
            "attribution_insights": [],
        }

    attributions = result.get("attributions", [])
    top_contributors = result.get("top_contributors", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"识别了 {len(top_contributors)} 个主要贡献因素"
    step["data"] = {
        "attribution_count": len(attributions),
        "top_contributor_count": len(top_contributors),
    }

    return {
        "attributions": attributions,
        "top_contributors": top_contributors,
        "contribution_breakdown": result.get("contribution_breakdown", {}),
        "attribution_insights": result.get("attribution_insights", []),
        "steps": [step],
    }
