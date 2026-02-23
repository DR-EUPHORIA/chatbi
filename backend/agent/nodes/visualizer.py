"""可视化 Node — 根据数据分析结果生成 ECharts 图表配置"""

import json
import re
from agent.state import AgentState, IntentType, NodeStatus
from agent.prompts.visualizer import VISUALIZER_SYSTEM_PROMPT, VISUALIZER_USER_PROMPT
from agent.llm import get_llm


def visualizer_node(state: AgentState) -> dict:
    """根据数据分析结果推荐图表类型并生成 ECharts 配置"""

    user_message = state.get("user_message", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    analysis_result = state.get("analysis_result", {})
    intent = state.get("intent", "data_query")

    step = {
        "node_name": "visualizer",
        "status": NodeStatus.RUNNING.value,
        "title": "生成图表",
        "detail": "正在生成可视化图表...",
        "data": {},
    }

    data_preview = sql_result[:50]
    data_str = json.dumps(data_preview, ensure_ascii=False, indent=2)
    columns_str = json.dumps(sql_result_columns, ensure_ascii=False)
    analysis_str = json.dumps(analysis_result, ensure_ascii=False, indent=2)

    llm = get_llm()
    prompt = VISUALIZER_USER_PROMPT.format(
        user_message=user_message,
        analysis_result=analysis_str,
        columns=columns_str,
        data=data_str,
    )

    response = llm.invoke([
        {"role": "system", "content": VISUALIZER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        # 尝试从 markdown 代码块中提取
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response.content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                result = None
        if not isinstance(result, dict):
            result = _generate_fallback_chart(sql_result_columns, sql_result)

    chart_type = result.get("chart_type", "bar")
    chart_config = result.get("echarts_option", {})

    updates: dict = {
        "chart_type": chart_type,
        "chart_config": chart_config,
    }

    if intent == IntentType.DASHBOARD.value:
        updates["dashboard_config"] = _build_dashboard_config(
            analysis_result, state.get("report_title", ""), result
        )

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"已生成{_chart_type_label(chart_type)}"
    step["data"] = {
        "chart_type": chart_type,
        "chart_title": result.get("chart_title", ""),
        "has_additional_charts": len(result.get("additional_charts", [])) > 0,
    }

    updates["steps"] = [step]
    return updates


def _generate_fallback_chart(columns: list[str], data: list[dict]) -> dict:
    """当 LLM 输出无法解析时，生成一个基于数据的默认柱状图"""
    data = data[:20]

    if len(columns) < 2 or not data:
        return {"chart_type": "bar", "chart_title": "数据概览", "echarts_option": {}}

    x_field = columns[0]
    y_field = columns[1]

    return {
        "chart_type": "bar",
        "chart_title": f"{y_field} 分布",
        "chart_description": f"按 {x_field} 展示 {y_field}",
        "echarts_option": {
            "title": {"text": f"{y_field} 分布", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": [str(row.get(x_field, "")) for row in data],
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "name": y_field,
                    "type": "bar",
                    "data": [row.get(y_field, 0) for row in data],
                    "itemStyle": {"color": "#5B8FF9"},
                }
            ],
        },
    }


def _build_dashboard_config(analysis: dict, report_title: str, chart_result: dict) -> dict:
    """构建数字化大屏配置"""
    key_metrics = analysis.get("key_metrics", {})
    widgets = []

    for metric_name, metric_value in key_metrics.items():
        widgets.append({
            "type": "number_card",
            "title": metric_name,
            "value": metric_value,
            "position": {"x": 0, "y": 0, "w": 3, "h": 2},
        })

    widgets.append({
        "type": "chart",
        "title": chart_result.get("chart_title", "数据图表"),
        "echarts_option": chart_result.get("echarts_option", {}),
        "position": {"x": 0, "y": 2, "w": 8, "h": 6},
    })

    for idx, additional in enumerate(chart_result.get("additional_charts", [])):
        widgets.append({
            "type": "chart",
            "title": additional.get("chart_title", f"图表 {idx + 2}"),
            "echarts_option": additional.get("echarts_option", {}),
            "position": {"x": 8, "y": idx * 4, "w": 4, "h": 4},
        })

    return {
        "theme": "tech_blue",
        "title": report_title or "数据大屏",
        "widgets": widgets,
    }


def _chart_type_label(chart_type: str) -> str:
    """图表类型的中文标签"""
    labels = {
        "line": "折线图",
        "bar": "柱状图",
        "pie": "饼图",
        "radar": "雷达图",
        "scatter": "散点图",
        "funnel": "漏斗图",
        "gauge": "仪表盘",
        "map": "地图",
        "number_card": "数字卡片",
    }
    return labels.get(chart_type, chart_type)