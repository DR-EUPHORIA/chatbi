"""图表配置生成工具 — 辅助生成 ECharts 配置"""

from typing import Any


# 专业配色方案
COLOR_SCHEMES = {
    "default": ["#5B8FF9", "#5AD8A6", "#5D7092", "#F6BD16", "#E86452", "#6DC8EC", "#945FB9", "#FF9845", "#1E9493", "#FF99C3"],
    "blue_purple": ["#667eea", "#764ba2", "#6B8DD6", "#8E7CC3", "#5B8FF9", "#9B8FE8", "#7EC2F3", "#B8ACF6", "#5AD8A6", "#F6BD16"],
    "tech_dark": ["#00D4FF", "#00FF88", "#FF6B6B", "#FFD93D", "#6C5CE7", "#A29BFE", "#FD79A8", "#FDCB6E", "#00B894", "#E17055"],
    "warm": ["#FF6B6B", "#FFA07A", "#FFD93D", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9", "#F8C471", "#82E0AA", "#F1948A"],
}


def get_color_scheme(scheme_name: str = "default") -> list[str]:
    """获取配色方案"""
    return COLOR_SCHEMES.get(scheme_name, COLOR_SCHEMES["default"])


def build_line_chart(title: str, x_data: list, y_data: list, y_name: str = "", scheme: str = "default") -> dict:
    """构建折线图配置"""
    colors = get_color_scheme(scheme)
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": x_data},
        "yAxis": {"type": "value", "name": y_name},
        "series": [{"name": y_name, "type": "line", "data": y_data, "smooth": True, "itemStyle": {"color": colors[0]}}],
        "color": colors,
    }


def build_bar_chart(title: str, x_data: list, y_data: list, y_name: str = "", horizontal: bool = False, scheme: str = "default") -> dict:
    """构建柱状图配置"""
    colors = get_color_scheme(scheme)
    if horizontal:
        return {
            "title": {"text": title, "left": "center"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "value"},
            "yAxis": {"type": "category", "data": x_data},
            "series": [{"name": y_name, "type": "bar", "data": y_data, "itemStyle": {"color": colors[0]}}],
            "color": colors,
        }
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": x_data, "axisLabel": {"rotate": 30}},
        "yAxis": {"type": "value", "name": y_name},
        "series": [{"name": y_name, "type": "bar", "data": y_data, "itemStyle": {"color": colors[0]}}],
        "color": colors,
    }


def build_pie_chart(title: str, data: list[dict[str, Any]], scheme: str = "default") -> dict:
    """构建饼图/环形图配置"""
    colors = get_color_scheme(scheme)
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c} ({d}%)"},
        "legend": {"orient": "vertical", "left": "left", "top": "middle"},
        "series": [{
            "name": title,
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": True,
            "itemStyle": {"borderRadius": 10, "borderColor": "#fff", "borderWidth": 2},
            "label": {"show": True, "formatter": "{b}: {d}%"},
            "data": data,
        }],
        "color": colors,
    }


def build_radar_chart(title: str, indicators: list[dict], data: list[dict], scheme: str = "default") -> dict:
    """构建雷达图配置"""
    colors = get_color_scheme(scheme)
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {},
        "radar": {"indicator": indicators},
        "series": [{"type": "radar", "data": data}],
        "color": colors,
    }


def build_gauge_chart(title: str, value: float, max_value: float = 100, scheme: str = "default") -> dict:
    """构建仪表盘配置"""
    colors = get_color_scheme(scheme)
    return {
        "title": {"text": title, "left": "center"},
        "series": [{
            "type": "gauge",
            "detail": {"formatter": "{value}%"},
            "data": [{"value": value, "name": title}],
            "max": max_value,
            "axisLine": {"lineStyle": {"width": 15, "color": [[0.3, colors[4]], [0.7, colors[3]], [1, colors[0]]]}},
        }],
    }


def build_funnel_chart(title: str, data: list[dict[str, Any]], scheme: str = "default") -> dict:
    """构建漏斗图配置"""
    colors = get_color_scheme(scheme)
    return {
        "title": {"text": title, "left": "center"},
        "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
        "series": [{
            "name": title,
            "type": "funnel",
            "left": "10%",
            "width": "80%",
            "label": {"show": True, "position": "inside"},
            "data": data,
        }],
        "color": colors,
    }
