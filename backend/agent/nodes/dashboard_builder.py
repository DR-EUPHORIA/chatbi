"""仪表盘构建 Node — 构建多图表仪表盘配置"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.dashboard_builder import DASHBOARD_BUILDER_SYSTEM_PROMPT, DASHBOARD_BUILDER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def dashboard_builder_node(state: AgentState) -> dict:
    """根据分析结果构建多图表仪表盘配置"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    analysis_result = state.get("analysis_result", {})
    key_insights = state.get("key_insights", [])
    recommended_chart = state.get("recommended_chart", "")

    step = {
        "node_name": "dashboard_builder",
        "status": NodeStatus.RUNNING.value,
        "title": "仪表盘构建",
        "detail": "正在构建仪表盘配置...",
        "data": {},
    }

    data_preview = sql_result[:30]
    
    llm = get_llm()
    prompt = safe_format_prompt(DASHBOARD_BUILDER_USER_PROMPT, 
        user_message=user_message,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data_sample=json.dumps(data_preview, ensure_ascii=False, indent=2),
        analysis_result=json.dumps(analysis_result, ensure_ascii=False),
        key_insights=json.dumps(key_insights, ensure_ascii=False),
        recommended_chart=recommended_chart,
    )

    response = llm.invoke([
        {"role": "system", "content": DASHBOARD_BUILDER_SYSTEM_PROMPT},
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
            "dashboard_title": "数据分析仪表盘",
            "layout": "grid",
            "widgets": [],
            "filters": [],
        }

    widgets = result.get("widgets", [])
    
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"构建了包含 {len(widgets)} 个组件的仪表盘"
    step["data"] = {
        "dashboard_title": result.get("dashboard_title", ""),
        "widget_count": len(widgets),
        "layout": result.get("layout", "grid"),
    }

    return {
        "dashboard_config": result,
        "dashboard_title": result.get("dashboard_title", ""),
        "dashboard_widgets": widgets,
        "dashboard_filters": result.get("filters", []),
        "steps": [step],
    }
