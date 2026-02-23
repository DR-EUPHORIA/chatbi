def _serialize_state(state: dict) -> dict:
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
