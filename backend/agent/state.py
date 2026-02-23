"""Agent 状态定义 — LangGraph 工作流中流转的数据结构"""

from __future__ import annotations

from enum import Enum
from typing import Any, Annotated, TypedDict, List, Dict, Optional


class IntentType(str, Enum):
    """用户意图类型"""
    DATA_QUERY = "data_query"
    FILE_ANALYSIS = "file_analysis"
    REPORT = "report"
    DASHBOARD = "dashboard"
    CHAT = "chat"
    UNCLEAR = "unclear"


class QueryType(str, Enum):
    """查询类型"""
    AGGREGATION = "aggregation"
    TREND = "trend"
    COMPARISON = "comparison"
    DISTRIBUTION = "distribution"
    CORRELATION = "correlation"
    RANKING = "ranking"
    DETAIL = "detail"
    UNKNOWN = "unknown"


class NodeStatus(str, Enum):
    """节点执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    WAITING_USER = "waiting_user"


def _append_steps(existing: list, new: list) -> list:
    """LangGraph reducer：steps 字段使用追加策略"""
    return (existing or []) + (new or [])


class AgentState(TypedDict, total=False):
    """Agent 状态定义 — 包含所有节点间流转的数据字段"""
    
    # ══════════════════════════════════════════════════════════════════════════
    # 基础输入字段
    # ══════════════════════════════════════════════════════════════════════════
    user_message: str                          # 用户原始问题
    session_id: str                            # 会话 ID
    dataset_id: str                            # 数据集 ID
    conversation_history: List[Dict]           # 对话历史
    
    # ══════════════════════════════════════════════════════════════════════════
    # Gate Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    is_clear: bool                             # 问题是否清晰
    gate_feedback: str                         # 门控反馈信息
    
    # ══════════════════════════════════════════════════════════════════════════
    # Router Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    intent: str                                # 用户意图
    
    # ══════════════════════════════════════════════════════════════════════════
    # Entity Extractor Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    extracted_entities: Dict                   # 提取的所有实体
    time_entities: List[Dict]                  # 时间实体
    dimension_entities: List[Dict]             # 维度实体
    metric_entities: List[Dict]                # 指标实体
    filter_entities: List[Dict]                # 过滤条件实体
    
    # ══════════════════════════════════════════════════════════════════════════
    # Query Rewriter Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    rewritten_query: str                       # 改写后的查询
    query_type: str                            # 查询类型
    query_confidence: float                    # 查询置信度
    
    # ══════════════════════════════════════════════════════════════════════════
    # Planner Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    plan: List[Dict]                           # 执行计划
    
    # ══════════════════════════════════════════════════════════════════════════
    # Schema Search Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    matched_tables: List[Dict]                 # 匹配的表信息
    
    # ══════════════════════════════════════════════════════════════════════════
    # Term Mapper Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    term_mappings: Dict                        # 术语映射
    unmapped_terms: List[str]                  # 未映射的术语
    mapping_confidence: Dict                   # 映射置信度
    mapping_notes: List[str]                   # 映射备注
    glossary: Dict                             # 业务术语表
    
    # ══════════════════════════════════════════════════════════════════════════
    # Column Selector Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    selected_columns: List[Dict]               # 选中的列
    dimension_columns: List[str]               # 维度列
    metric_columns: List[str]                  # 指标列
    filter_columns: List[str]                  # 过滤列
    
    # ══════════════════════════════════════════════════════════════════════════
    # Clarifier Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    has_ambiguity: bool                        # 是否有歧义
    clarify_options: List[Dict]                # 澄清选项
    
    # ══════════════════════════════════════════════════════════════════════════
    # SQL Generator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    generated_sql: str                         # 生成的 SQL
    sql_explanation: str                       # SQL 解释
    
    # ══════════════════════════════════════════════════════════════════════════
    # SQL Validator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    sql_is_valid: bool                         # SQL 是否有效
    sql_syntax_errors: List[str]               # 语法错误
    sql_semantic_warnings: List[str]           # 语义警告
    sql_suggestions: List[str]                 # SQL 建议
    
    # ══════════════════════════════════════════════════════════════════════════
    # SQL Optimizer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    sql_optimizations: List[str]               # 应用的优化
    sql_performance_notes: List[str]           # 性能备注
    
    # ══════════════════════════════════════════════════════════════════════════
    # SQL Executor Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    sql_result: List[Dict]                     # SQL 执行结果
    sql_result_columns: List[str]              # 结果列名
    sql_error: str                             # SQL 错误信息
    sql_retry_count: int                       # SQL 重试次数
    
    # ══════════════════════════════════════════════════════════════════════════
    # SQL Fixer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    fixed_sql: str                             # 修复后的 SQL
    fix_explanation: str                       # 修复说明
    
    # ══════════════════════════════════════════════════════════════════════════
    # Result Validator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    result_is_valid: bool                      # 结果是否有效
    result_validation_issues: List[str]        # 验证问题
    data_quality_score: float                  # 数据质量分数
    result_recommendations: List[str]          # 结果建议
    
    # ══════════════════════════════════════════════════════════════════════════
    # Data Cleaner Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    data_quality_issues: List[Dict]            # 数据质量问题
    cleaning_actions: List[Dict]               # 清洗操作
    cleaned_data_summary: Dict                 # 清洗后数据摘要
    
    # ══════════════════════════════════════════════════════════════════════════
    # Metric Calculator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    calculated_metrics: Dict                   # 计算的指标
    metric_definitions: List[Dict]             # 指标定义
    metric_insights: List[str]                 # 指标洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Analyzer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    analysis_result: Dict                      # 分析结果
    
    # ══════════════════════════════════════════════════════════════════════════
    # Trend Analyzer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    trend_analysis: Dict                       # 趋势分析结果
    trend_direction: str                       # 趋势方向
    trend_strength: float                      # 趋势强度
    seasonality: Optional[Dict]                # 季节性
    turning_points: List[Dict]                 # 转折点
    trend_insights: List[str]                  # 趋势洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Anomaly Detector Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    anomalies: List[Dict]                      # 异常
    outliers: List[Dict]                       # 离群点
    anomaly_score: float                       # 异常分数
    anomaly_insights: List[str]                # 异常洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Comparison Analyzer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    comparison_analysis: Dict                  # 对比分析结果
    comparison_type: str                       # 对比类型
    comparisons: List[Dict]                    # 对比项
    rankings: List[Dict]                       # 排名
    comparison_insights: List[str]             # 对比洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Correlation Analyzer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    correlations: List[Dict]                   # 相关性
    strong_correlations: List[Dict]            # 强相关
    potential_causations: List[Dict]           # 潜在因果
    correlation_insights: List[str]            # 相关性洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Distribution Analyzer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    distribution_stats: Dict                   # 分布统计
    distribution_type: str                     # 分布类型
    skewness: float                            # 偏度
    kurtosis: float                            # 峰度
    distribution_insights: List[str]           # 分布洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Attribution Analyzer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    attributions: List[Dict]                   # 归因
    top_contributors: List[Dict]               # 主要贡献者
    contribution_breakdown: Dict               # 贡献分解
    attribution_insights: List[str]            # 归因洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Forecast Generator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    forecasts: List[Dict]                      # 预测结果
    forecast_method: str                       # 预测方法
    confidence_interval: Dict                  # 置信区间
    forecast_insights: List[str]               # 预测洞察
    forecast_assumptions: List[str]            # 预测假设
    
    # ══════════════════════════════════════════════════════════════════════════
    # KPI Monitor Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    kpi_status: List[Dict]                     # KPI 状态
    kpi_alerts: List[Dict]                     # KPI 告警
    kpi_health_score: float                    # KPI 健康分数
    kpi_insights: List[str]                    # KPI 洞察
    
    # ══════════════════════════════════════════════════════════════════════════
    # Insight Extractor Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    key_insights: List[Dict]                   # 关键洞察
    insight_priority: List[str]                # 洞察优先级
    action_items: List[Dict]                   # 行动项
    follow_up_questions: List[str]             # 后续问题
    
    # ══════════════════════════════════════════════════════════════════════════
    # Chart Recommender Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    recommended_chart: str                     # 推荐的图表类型
    chart_alternatives: List[str]              # 备选图表
    chart_reason: str                          # 推荐原因
    visualization_config: Dict                 # 可视化配置
    
    # ══════════════════════════════════════════════════════════════════════════
    # Visualizer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    chart_type: str                            # 图表类型
    chart_config: Dict                         # 图表配置
    
    # ══════════════════════════════════════════════════════════════════════════
    # Dashboard Builder Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    dashboard_config: Dict                     # 仪表盘配置
    dashboard_title: str                       # 仪表盘标题
    dashboard_widgets: List[Dict]              # 仪表盘组件
    dashboard_filters: List[Dict]              # 仪表盘过滤器
    
    # ══════════════════════════════════════════════════════════════════════════
    # Summary Generator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    executive_summary: str                     # 执行摘要
    summary_key_points: List[str]              # 关键要点
    summary_conclusion: str                    # 结论
    
    # ══════════════════════════════════════════════════════════════════════════
    # Recommendation Generator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    recommendations: List[Dict]                # 建议
    priority_actions: List[Dict]               # 优先行动
    risk_mitigations: List[Dict]               # 风险缓解
    next_steps: List[str]                      # 下一步
    
    # ══════════════════════════════════════════════════════════════════════════
    # Narrative Generator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    narrative: Dict                            # 叙事内容
    narrative_type: str                        # 叙事类型
    narrative_title: str                       # 叙事标题
    narrative_sections: List[Dict]             # 叙事章节
    narrative_summary: str                     # 叙事摘要
    
    # ══════════════════════════════════════════════════════════════════════════
    # Answer Generator Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    final_answer: str                          # 最终回答
    answer_type: str                           # 回答类型
    answer_confidence: float                   # 回答置信度
    answer_sources: List[str]                  # 回答来源
    
    # ══════════════════════════════════════════════════════════════════════════
    # Reporter Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    report_title: str                          # 报告标题
    report_summary: str                        # 报告摘要
    report_insights: List[str]                 # 报告洞察
    report_html: str                           # HTML 报告
    report_markdown: str                       # Markdown 报告
    excel_path: str                            # Excel 路径
    ppt_path: str                              # PPT 路径
    
    # ══════════════════════════════════════════════════════════════════════════
    # File Parser Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    file_path: str                             # 文件路径
    file_content: str                          # 文件内容
    file_type: str                             # 文件类型
    parsed_file_structure: Dict                # 解析的文件结构
    parsed_columns: List[str]                  # 解析的列
    parsed_row_count: int                      # 解析的行数
    parsed_data_types: Dict                    # 解析的数据类型
    parsing_notes: List[str]                   # 解析备注
    
    # ══════════════════════════════════════════════════════════════════════════
    # File Analyzer Node 输出
    # ══════════════════════════════════════════════════════════════════════════
    file_summary: str                          # 文件摘要
    file_key_findings: List[Dict]              # 文件关键发现
    file_data_quality: Dict                    # 文件数据质量
    recommended_analyses: List[str]            # 推荐的分析
    
    # ══════════════════════════════════════════════════════════════════════════
    # 通用字段
    # ══════════════════════════════════════════════════════════════════════════
    steps: Annotated[List[Dict], _append_steps]  # 执行步骤（使用追加策略）
    error: str                                 # 错误信息