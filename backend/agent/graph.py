"""LangGraph 工作流定义 — ChatBI Agent 的核心编排逻辑"""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator, Any

from langgraph.graph import StateGraph, END

from agent.state import AgentState, IntentType, NodeStatus

# ══════════════════════════════════════════════════════════════════════════════
# 核心流程 Node
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.gate import gate_node
from agent.nodes.router import router_node
from agent.nodes.planner import planner_node
from agent.nodes.schema_search import schema_search_node
from agent.nodes.clarifier import clarifier_node
from agent.nodes.sql_generator import sql_generator_node
from agent.nodes.sql_executor import sql_executor_node
from agent.nodes.sql_fixer import sql_fixer_node
from agent.nodes.analyzer import analyzer_node
from agent.nodes.visualizer import visualizer_node
from agent.nodes.reporter import reporter_node

# ══════════════════════════════════════════════════════════════════════════════
# 理解层 Node — 深入理解用户意图
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.entity_extractor import entity_extractor_node
from agent.nodes.query_rewriter import query_rewriter_node
from agent.nodes.term_mapper import term_mapper_node
from agent.nodes.column_selector import column_selector_node

# ══════════════════════════════════════════════════════════════════════════════
# SQL 处理层 Node — SQL 生成、验证、优化
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.sql_validator import sql_validator_node
from agent.nodes.sql_optimizer import sql_optimizer_node
from agent.nodes.result_validator import result_validator_node

# ══════════════════════════════════════════════════════════════════════════════
# 数据处理层 Node — 数据清洗和指标计算
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.data_cleaner import data_cleaner_node
from agent.nodes.metric_calculator import metric_calculator_node

# ══════════════════════════════════════════════════════════════════════════════
# 分析层 Node — 多维度数据分析
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.trend_analyzer import trend_analyzer_node
from agent.nodes.anomaly_detector import anomaly_detector_node
from agent.nodes.comparison_analyzer import comparison_analyzer_node
from agent.nodes.correlation_analyzer import correlation_analyzer_node
from agent.nodes.distribution_analyzer import distribution_analyzer_node
from agent.nodes.attribution_analyzer import attribution_analyzer_node
from agent.nodes.forecast_generator import forecast_generator_node
from agent.nodes.kpi_monitor import kpi_monitor_node

# ══════════════════════════════════════════════════════════════════════════════
# 洞察层 Node — 提取洞察和生成建议
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.insight_extractor import insight_extractor_node
from agent.nodes.recommendation_generator import recommendation_generator_node

# ══════════════════════════════════════════════════════════════════════════════
# 可视化层 Node — 图表推荐和仪表盘构建
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.chart_recommender import chart_recommender_node
from agent.nodes.dashboard_builder import dashboard_builder_node

# ══════════════════════════════════════════════════════════════════════════════
# 输出层 Node — 生成最终输出
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.summary_generator import summary_generator_node
from agent.nodes.narrative_generator import narrative_generator_node
from agent.nodes.answer_generator import answer_generator_node

# ══════════════════════════════════════════════════════════════════════════════
# 文件处理层 Node — 处理上传文件
# ══════════════════════════════════════════════════════════════════════════════
from agent.nodes.file_parser import file_parser_node
from agent.nodes.file_analyzer import file_analyzer_node

logger = logging.getLogger(__name__)

# ── 条件路由函数（AgentState 是 TypedDict，用 dict.get 访问） ──


def after_gate(state: AgentState) -> str:
    """门控后的路由：清晰则进入路由，不清晰则结束并返回引导"""
    if state.get("is_clear", False):
        return "router"
    return END


def after_router(state: AgentState) -> str:
    """意图路由后的分发"""
    intent = state.get("intent", "")
    if intent == IntentType.CHAT.value:
        return END
    if intent == IntentType.FILE_ANALYSIS.value:
        return "file_parser"
    return "entity_extractor"


def after_clarifier(state: AgentState) -> str:
    """歧义检测后的路由"""
    if state.get("has_ambiguity", False):
        return END
    return "sql_generator"


def after_sql_executor(state: AgentState) -> str:
    """SQL 执行后的路由：成功则验证结果，失败则修正"""
    sql_error = state.get("sql_error", "")
    retry_count = state.get("sql_retry_count", 0)
    if sql_error and retry_count < 3:
        return "sql_fixer"
    if sql_error:
        return END
    return "result_validator"


def after_entity_extractor(state: AgentState) -> str:
    """实体抽取后的路由"""
    return "query_rewriter"


def after_query_rewriter(state: AgentState) -> str:
    """查询改写后的路由"""
    return "planner"


def after_term_mapper(state: AgentState) -> str:
    """术语映射后的路由"""
    unmapped = state.get("unmapped_terms", [])
    if unmapped and len(unmapped) > 3:
        return "clarifier"
    return "column_selector"


def after_column_selector(state: AgentState) -> str:
    """列选择后的路由"""
    return "clarifier"


def after_sql_validator(state: AgentState) -> str:
    """SQL 验证后的路由"""
    is_valid = state.get("sql_is_valid", True)
    retry_count = state.get("sql_retry_count", 0)
    if not is_valid:
        # 避免 sql_validator <-> sql_fixer 无限循环
        if retry_count >= 3:
            return END
        return "sql_fixer"
    return "sql_optimizer"


def after_sql_optimizer(state: AgentState) -> str:
    """SQL 优化后的路由"""
    return "sql_executor"


def after_result_validator(state: AgentState) -> str:
    """结果验证后的路由"""
    is_valid = state.get("result_is_valid", True)
    if not is_valid:
        retry_count = state.get("sql_retry_count", 0)
        if retry_count < 2:
            return "sql_fixer"
    return "data_cleaner"


def after_data_cleaner(state: AgentState) -> str:
    """数据清洗后的路由"""
    return "metric_calculator"


def after_metric_calculator(state: AgentState) -> str:
    """指标计算后的路由"""
    return "analyzer"


def after_analyzer_enhanced(state: AgentState) -> str:
    """增强分析后的路由：根据查询类型选择分析路径"""
    query_type = state.get("query_type", "unknown")
    
    if query_type == "trend":
        return "trend_analyzer"
    elif query_type == "comparison":
        return "comparison_analyzer"
    elif query_type == "distribution":
        return "distribution_analyzer"
    elif query_type == "correlation":
        return "correlation_analyzer"
    else:
        return "trend_analyzer"


def after_trend_analyzer(state: AgentState) -> str:
    """趋势分析后的路由"""
    return "anomaly_detector"


def after_anomaly_detector(state: AgentState) -> str:
    """异常检测后的路由"""
    return "insight_extractor"


def after_comparison_analyzer(state: AgentState) -> str:
    """对比分析后的路由"""
    return "attribution_analyzer"


def after_attribution_analyzer(state: AgentState) -> str:
    """归因分析后的路由"""
    return "insight_extractor"


def after_distribution_analyzer(state: AgentState) -> str:
    """分布分析后的路由"""
    return "insight_extractor"


def after_correlation_analyzer(state: AgentState) -> str:
    """相关性分析后的路由"""
    return "forecast_generator"


def after_forecast_generator(state: AgentState) -> str:
    """预测生成后的路由"""
    return "insight_extractor"


def after_insight_extractor(state: AgentState) -> str:
    """洞察提取后的路由"""
    return "recommendation_generator"


def after_recommendation_generator(state: AgentState) -> str:
    """建议生成后的路由"""
    return "chart_recommender"


def after_chart_recommender(state: AgentState) -> str:
    """图表推荐后的路由"""
    return "visualizer"


def after_visualizer_enhanced(state: AgentState) -> str:
    """可视化后的路由：根据意图选择输出路径"""
    intent = state.get("intent", "")
    if intent == IntentType.DASHBOARD.value:
        return "dashboard_builder"
    return "summary_generator"


def after_dashboard_builder(state: AgentState) -> str:
    """仪表盘构建后的路由"""
    return "summary_generator"


def after_summary_generator(state: AgentState) -> str:
    """摘要生成后的路由"""
    return "narrative_generator"


def after_narrative_generator(state: AgentState) -> str:
    """叙事生成后的路由"""
    return "answer_generator"


def after_answer_generator(state: AgentState) -> str:
    """答案生成后的路由"""
    return "reporter"


def after_file_parser(state: AgentState) -> str:
    """文件解析后的路由"""
    return "file_analyzer"


def after_file_analyzer(state: AgentState) -> str:
    """文件分析后的路由"""
    return "insight_extractor"


def build_graph() -> StateGraph:
    """构建 ChatBI Agent 的 LangGraph 工作流
    
    工作流架构：
    
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           理解层 (Understanding)                         │
    │  gate → router → entity_extractor → query_rewriter → planner            │
    └─────────────────────────────────────────────────────────────────────────┘
                                        ↓
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           映射层 (Mapping)                               │
    │  schema_search → term_mapper → column_selector → clarifier              │
    └─────────────────────────────────────────────────────────────────────────┘
                                        ↓
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           SQL 层 (SQL Processing)                        │
    │  sql_generator → sql_validator → sql_optimizer → sql_executor           │
    │                                                       ↓                 │
    │                                               sql_fixer (if error)      │
    └─────────────────────────────────────────────────────────────────────────┘
                                        ↓
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           数据层 (Data Processing)                       │
    │  result_validator → data_cleaner → metric_calculator                    │
    └─────────────────────────────────────────────────────────────────────────┘
                                        ↓
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           分析层 (Analysis)                              │
    │  analyzer → trend_analyzer / comparison_analyzer / distribution_analyzer│
    │           → anomaly_detector / attribution_analyzer / correlation_analyzer│
    │           → forecast_generator                                          │
    └─────────────────────────────────────────────────────────────────────────┘
                                        ↓
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           洞察层 (Insight)                               │
    │  insight_extractor → recommendation_generator                           │
    └─────────────────────────────────────────────────────────────────────────┘
                                        ↓
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           可视化层 (Visualization)                       │
    │  chart_recommender → visualizer → dashboard_builder                     │
    └─────────────────────────────────────────────────────────────────────────┘
                                        ↓
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                           输出层 (Output)                                │
    │  summary_generator → narrative_generator → answer_generator → reporter │
    └─────────────────────────────────────────────────────────────────────────┘
    """

    workflow = StateGraph(AgentState)

    # ══════════════════════════════════════════════════════════════════════════
    # 注册所有 Node
    # ══════════════════════════════════════════════════════════════════════════
    
    # 核心流程 Node
    workflow.add_node("gate", gate_node)
    workflow.add_node("router", router_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("schema_search", schema_search_node)
    workflow.add_node("clarifier", clarifier_node)
    workflow.add_node("sql_generator", sql_generator_node)
    workflow.add_node("sql_executor", sql_executor_node)
    workflow.add_node("sql_fixer", sql_fixer_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("visualizer", visualizer_node)
    workflow.add_node("reporter", reporter_node)
    
    # 理解层 Node
    workflow.add_node("entity_extractor", entity_extractor_node)
    workflow.add_node("query_rewriter", query_rewriter_node)
    workflow.add_node("term_mapper", term_mapper_node)
    workflow.add_node("column_selector", column_selector_node)
    
    # SQL 处理层 Node
    workflow.add_node("sql_validator", sql_validator_node)
    workflow.add_node("sql_optimizer", sql_optimizer_node)
    workflow.add_node("result_validator", result_validator_node)
    
    # 数据处理层 Node
    workflow.add_node("data_cleaner", data_cleaner_node)
    workflow.add_node("metric_calculator", metric_calculator_node)
    
    # 分析层 Node
    workflow.add_node("trend_analyzer", trend_analyzer_node)
    workflow.add_node("anomaly_detector", anomaly_detector_node)
    workflow.add_node("comparison_analyzer", comparison_analyzer_node)
    workflow.add_node("correlation_analyzer", correlation_analyzer_node)
    workflow.add_node("distribution_analyzer", distribution_analyzer_node)
    workflow.add_node("attribution_analyzer", attribution_analyzer_node)
    workflow.add_node("forecast_generator", forecast_generator_node)
    workflow.add_node("kpi_monitor", kpi_monitor_node)
    
    # 洞察层 Node
    workflow.add_node("insight_extractor", insight_extractor_node)
    workflow.add_node("recommendation_generator", recommendation_generator_node)
    
    # 可视化层 Node
    workflow.add_node("chart_recommender", chart_recommender_node)
    workflow.add_node("dashboard_builder", dashboard_builder_node)
    
    # 输出层 Node
    workflow.add_node("summary_generator", summary_generator_node)
    workflow.add_node("narrative_generator", narrative_generator_node)
    workflow.add_node("answer_generator", answer_generator_node)
    
    # 文件处理层 Node
    workflow.add_node("file_parser", file_parser_node)
    workflow.add_node("file_analyzer", file_analyzer_node)

    # ══════════════════════════════════════════════════════════════════════════
    # 设置入口点
    # ══════════════════════════════════════════════════════════════════════════
    workflow.set_entry_point("gate")

    # ══════════════════════════════════════════════════════════════════════════
    # 定义边和条件路由
    # ══════════════════════════════════════════════════════════════════════════
    
    # 理解层路由
    workflow.add_conditional_edges("gate", after_gate)
    workflow.add_conditional_edges("router", after_router)
    workflow.add_edge("entity_extractor", "query_rewriter")
    workflow.add_edge("query_rewriter", "planner")
    
    # 映射层路由
    workflow.add_edge("planner", "schema_search")
    workflow.add_edge("schema_search", "term_mapper")
    workflow.add_conditional_edges("term_mapper", after_term_mapper)
    workflow.add_edge("column_selector", "clarifier")
    workflow.add_conditional_edges("clarifier", after_clarifier)
    
    # SQL 处理层路由
    workflow.add_edge("sql_generator", "sql_validator")
    workflow.add_conditional_edges("sql_validator", after_sql_validator)
    workflow.add_edge("sql_optimizer", "sql_executor")
    workflow.add_conditional_edges("sql_executor", after_sql_executor)
    workflow.add_edge("sql_fixer", "sql_validator")
    
    # 数据处理层路由
    workflow.add_edge("result_validator", "data_cleaner")
    workflow.add_edge("data_cleaner", "metric_calculator")
    workflow.add_edge("metric_calculator", "analyzer")
    
    # 分析层路由
    workflow.add_conditional_edges("analyzer", after_analyzer_enhanced)
    workflow.add_edge("trend_analyzer", "anomaly_detector")
    workflow.add_edge("anomaly_detector", "insight_extractor")
    workflow.add_edge("comparison_analyzer", "attribution_analyzer")
    workflow.add_edge("attribution_analyzer", "insight_extractor")
    workflow.add_edge("distribution_analyzer", "insight_extractor")
    workflow.add_edge("correlation_analyzer", "forecast_generator")
    workflow.add_edge("forecast_generator", "insight_extractor")
    
    # 洞察层路由
    workflow.add_edge("insight_extractor", "recommendation_generator")
    workflow.add_edge("recommendation_generator", "chart_recommender")
    
    # 可视化层路由
    workflow.add_edge("chart_recommender", "visualizer")
    workflow.add_conditional_edges("visualizer", after_visualizer_enhanced)
    workflow.add_edge("dashboard_builder", "summary_generator")
    
    # 输出层路由
    workflow.add_edge("summary_generator", "narrative_generator")
    workflow.add_edge("narrative_generator", "answer_generator")
    workflow.add_edge("answer_generator", "reporter")
    workflow.add_edge("reporter", END)
    
    # 文件处理路由
    workflow.add_edge("file_parser", "file_analyzer")
    workflow.add_edge("file_analyzer", "insight_extractor")

    return workflow


# ── 全局编译好的图 ──
_compiled_graph = None


def get_compiled_graph():
    """获取编译后的图（单例）"""
    global _compiled_graph
    if _compiled_graph is None:
        workflow = build_graph()
        _compiled_graph = workflow.compile()
    return _compiled_graph


async def run_agent_stream(
    message: str,
    session_id: str = "",
    dataset_id: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """流式执行 Agent，逐步 yield 事件给前端 SSE

    LangGraph astream(stream_mode="updates") 每个 node 完成后返回
    ``{node_name: partial_state_dict}``，其中 partial_state_dict 是该 node
    返回的增量更新字段。我们在这里维护一份累积 state 快照，每步推送给前端。
    """

    graph = get_compiled_graph()

    initial_state: AgentState = {
        "user_message": message,
        "session_id": session_id,
        "dataset_id": dataset_id or "demo_ecommerce",
    }

    # 累积 state 快照（用于最终 done 事件）
    accumulated_state: dict[str, Any] = dict(initial_state)

    yield {
        "type": "start",
        "data": {"session_id": session_id, "message": message},
    }

    try:
        async for event in graph.astream(
            initial_state,
            stream_mode="updates",
            config={"recursion_limit": 80},
        ):
            # event 格式: {node_name: partial_state_dict}
            for node_name, node_update in event.items():
                if not isinstance(node_update, dict):
                    continue

                # 合并增量更新到累积 state
                for key, value in node_update.items():
                    if key == "steps":
                        accumulated_state.setdefault("steps", [])
                        accumulated_state["steps"].extend(value or [])
                    else:
                        accumulated_state[key] = value

                # 提取本次 node 产出的 steps
                node_steps = node_update.get("steps", [])

                yield {
                    "type": "step",
                    "data": {
                        "node": node_name,
                        "status": "completed",
                        "steps": node_steps,
                        "state_snapshot": _serialize_state(accumulated_state),
                    },
                }

    except Exception as exc:
        logger.exception("Agent 执行异常")
        yield {
            "type": "error",
            "data": {"error": str(exc)},
        }
        return

    yield {
        "type": "done",
        "data": _serialize_state(accumulated_state),
    }


def _serialize_state(state: dict[str, Any]) -> dict[str, Any]:
    """将累积 state dict 序列化为前端需要的字段"""
    sql_result = state.get("sql_result", [])
    return {
        # 基础字段
        "intent": state.get("intent", ""),
        "is_clear": state.get("is_clear", False),
        "gate_feedback": state.get("gate_feedback", ""),
        
        # 理解层字段
        "extracted_entities": state.get("extracted_entities", {}),
        "rewritten_query": state.get("rewritten_query", ""),
        "query_type": state.get("query_type", ""),
        "query_confidence": state.get("query_confidence", 0.0),
        
        # 映射层字段
        "plan": state.get("plan", []),
        "matched_tables": state.get("matched_tables", []),
        "term_mappings": state.get("term_mappings", {}),
        "selected_columns": state.get("selected_columns", []),
        "has_ambiguity": state.get("has_ambiguity", False),
        "clarify_options": state.get("clarify_options", []),
        
        # SQL 层字段
        "generated_sql": state.get("generated_sql", ""),
        "sql_explanation": state.get("sql_explanation", ""),
        "sql_is_valid": state.get("sql_is_valid", True),
        "sql_optimizations": state.get("sql_optimizations", []),
        "sql_result": sql_result[:100] if isinstance(sql_result, list) else [],
        "sql_result_columns": state.get("sql_result_columns", []),
        "sql_error": state.get("sql_error", ""),
        
        # 数据处理层字段
        "result_is_valid": state.get("result_is_valid", True),
        "data_quality_score": state.get("data_quality_score", 0.0),
        "calculated_metrics": state.get("calculated_metrics", {}),
        
        # 分析层字段
        "analysis_result": state.get("analysis_result", {}),
        "trend_analysis": state.get("trend_analysis", {}),
        "trend_direction": state.get("trend_direction", ""),
        "anomalies": state.get("anomalies", []),
        "comparison_analysis": state.get("comparison_analysis", {}),
        "correlations": state.get("correlations", []),
        "distribution_stats": state.get("distribution_stats", {}),
        "attributions": state.get("attributions", []),
        "forecasts": state.get("forecasts", []),
        "kpi_status": state.get("kpi_status", []),
        "kpi_alerts": state.get("kpi_alerts", []),
        
        # 洞察层字段
        "key_insights": state.get("key_insights", []),
        "recommendations": state.get("recommendations", []),
        "action_items": state.get("action_items", []),
        "follow_up_questions": state.get("follow_up_questions", []),
        
        # 可视化层字段
        "recommended_chart": state.get("recommended_chart", ""),
        "chart_type": state.get("chart_type", ""),
        "chart_config": state.get("chart_config", {}),
        "dashboard_config": state.get("dashboard_config", {}),
        "dashboard_widgets": state.get("dashboard_widgets", []),
        
        # 输出层字段
        "executive_summary": state.get("executive_summary", ""),
        "narrative": state.get("narrative", {}),
        "narrative_title": state.get("narrative_title", ""),
        "final_answer": state.get("final_answer", ""),
        "answer_confidence": state.get("answer_confidence", 0.0),
        
        # 报告字段
        "report_title": state.get("report_title", ""),
        "report_summary": state.get("report_summary", ""),
        "report_insights": state.get("report_insights", []),
        "report_html": state.get("report_html", ""),
        "report_markdown": state.get("report_markdown", ""),
        "excel_path": state.get("excel_path", ""),
        "ppt_path": state.get("ppt_path", ""),
        
        # 文件处理字段
        "file_summary": state.get("file_summary", ""),
        "file_key_findings": state.get("file_key_findings", []),
        
        # 错误字段
        "error": state.get("error", ""),
    }
