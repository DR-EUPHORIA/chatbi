"""相关性分析 Node — 分析数据之间的相关性"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.correlation_analyzer import CORRELATION_ANALYZER_SYSTEM_PROMPT, CORRELATION_ANALYZER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def correlation_analyzer_node(state: AgentState) -> dict:
    """分析数据列之间的相关性，发现潜在的因果关系"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    metric_columns = state.get("metric_columns", [])

    step = {
        "node_name": "correlation_analyzer",
        "status": NodeStatus.RUNNING.value,
        "title": "相关性分析",
        "detail": "正在分析数据相关性...",
        "data": {},
    }

    data_preview = sql_result[:100]
    
    llm = get_llm()
    prompt = safe_format_prompt(CORRELATION_ANALYZER_USER_PROMPT, 
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data=json.dumps(data_preview, ensure_ascii=False, indent=2),
        metric_columns=json.dumps(metric_columns, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": CORRELATION_ANALYZER_SYSTEM_PROMPT},
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
            "correlations": [],
            "strong_correlations": [],
            "potential_causations": [],
            "correlation_insights": [],
        }

    correlations = result.get("correlations", [])
    strong_correlations = result.get("strong_correlations", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"发现 {len(strong_correlations)} 个强相关关系"
    step["data"] = {
        "total_correlations": len(correlations),
        "strong_correlation_count": len(strong_correlations),
    }

    return {
        "correlations": correlations,
        "strong_correlations": strong_correlations,
        "potential_causations": result.get("potential_causations", []),
        "correlation_insights": result.get("correlation_insights", []),
        "steps": [step],
    }
