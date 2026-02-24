"""Prompt formatting utilities."""

from __future__ import annotations

import inspect
import json
import os
from statistics import mean, median, pstdev
from typing import Any, Mapping


class _SafeFormatDict(dict):
    """Return an empty string for missing template keys."""

    def __missing__(self, key: str) -> str:
        return ""


def _json_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, indent=2)


def _normalize_rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _build_row_stats(rows: list[dict[str, Any]], columns: list[str]) -> tuple[dict[str, Any], dict[str, int], list[str]]:
    null_stats = {col: 0 for col in columns}
    numeric_cols: dict[str, list[float]] = {col: [] for col in columns}

    for row in rows:
        for col in columns:
            v = row.get(col)
            if v is None:
                null_stats[col] = null_stats.get(col, 0) + 1
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                numeric_cols[col].append(float(v))

    numeric_stats: dict[str, Any] = {}
    for col, vals in numeric_cols.items():
        if not vals:
            continue
        std = pstdev(vals) if len(vals) > 1 else 0.0
        numeric_stats[col] = {
            "min": min(vals),
            "max": max(vals),
            "mean": mean(vals),
            "median": median(vals),
            "std": std,
        }

    numeric_columns = [c for c in columns if c in numeric_stats]
    return numeric_stats, null_stats, numeric_columns


def _first_non_empty(*values: Any) -> Any:
    for v in values:
        if v is not None and v != "" and v != [] and v != {}:
            return v
    return None


def _infer_state_from_caller() -> Mapping[str, Any] | None:
    frame = inspect.currentframe()
    if not frame or not frame.f_back:
        return None
    caller_locals = frame.f_back.f_locals
    state = caller_locals.get("state")
    if isinstance(state, Mapping):
        return state
    return None


def _build_common_context(state: Mapping[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    ctx: dict[str, Any] = {}

    rows = _normalize_rows(_first_non_empty(kwargs.get("sql_result"), state.get("sql_result"), state.get("data")))
    columns = _first_non_empty(kwargs.get("columns"), state.get("sql_result_columns"), [])
    if isinstance(columns, str):
        try:
            columns = json.loads(columns)
        except Exception:
            columns = []
    if not isinstance(columns, list):
        columns = []
    if not columns and rows:
        columns = list(rows[0].keys())

    row_count = len(rows)
    column_count = len(columns)
    sample_rows = rows[:50]
    sample_rows_20 = rows[:20]

    numeric_stats, null_stats, numeric_columns = _build_row_stats(rows, columns)

    time_col = ""
    for col in columns:
        lc = str(col).lower()
        if any(x in lc for x in ("time", "date", "day", "month", "year")):
            time_col = col
            break
    value_col = numeric_columns[0] if numeric_columns else (columns[1] if len(columns) > 1 else (columns[0] if columns else ""))

    if time_col and value_col:
        time_series_data = [
            {"time": row.get(time_col), "value": row.get(value_col)}
            for row in rows[:100]
        ]
    else:
        time_series_data = sample_rows

    analysis_result = _first_non_empty(kwargs.get("analysis_result"), state.get("analysis_result"), {})
    chart_info = {
        "recommended_chart": state.get("recommended_chart", ""),
        "chart_type": state.get("chart_type", ""),
        "chart_config": state.get("chart_config", {}),
    }

    key_insights = _first_non_empty(
        state.get("key_insights"),
        state.get("trend_insights"),
        state.get("comparison_insights"),
        state.get("anomaly_insights"),
        [],
    )
    if isinstance(key_insights, list):
        insight_text = [str(i.get("insight", i)) if isinstance(i, dict) else str(i) for i in key_insights]
    else:
        insight_text = [str(key_insights)]

    metric_entities = state.get("metric_entities", [])
    if isinstance(metric_entities, list) and metric_entities:
        first_metric = metric_entities[0]
        if isinstance(first_metric, dict):
            target_metric = first_metric.get("name") or first_metric.get("raw_text") or "指标"
        else:
            target_metric = str(first_metric)
    else:
        target_metric = "指标"

    time_entities = state.get("time_entities", [])
    time_range = "当前周期"
    if isinstance(time_entities, list) and time_entities:
        t0 = time_entities[0]
        if isinstance(t0, dict):
            time_range = str(t0.get("raw_text") or t0.get("type") or "当前周期")

    half = max(1, len(sample_rows) // 2) if sample_rows else 0
    base_data = sample_rows[:half] if half else []
    compare_data = sample_rows[half:] if half else []

    numeric_values: list[float] = []
    if numeric_columns:
        col = numeric_columns[0]
        for row in rows:
            v = row.get(col)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                numeric_values.append(float(v))
    current_value = numeric_values[-1] if numeric_values else 0.0
    base_value = numeric_values[0] if numeric_values else 0.0
    change_rate = (current_value - base_value) / base_value if base_value else 0.0

    file_path = str(_first_non_empty(kwargs.get("file_path"), state.get("file_path"), ""))
    file_content = str(_first_non_empty(state.get("file_content"), ""))
    parsed_file = _first_non_empty(state.get("parsed_file_structure"), {})

    ctx.update(
        {
            "sql": _first_non_empty(kwargs.get("generated_sql"), kwargs.get("original_sql"), state.get("generated_sql"), ""),
            "schema_context": _first_non_empty(kwargs.get("matched_tables"), state.get("schema_context"), []),
            "data": _json_text(_first_non_empty(kwargs.get("data"), sample_rows, [])),
            "data_sample": _json_text(_first_non_empty(kwargs.get("data_sample"), sample_rows_20, [])),
            "historical_data": _json_text(sample_rows),
            "time_series_data": _json_text(time_series_data),
            "current_data": _json_text(sample_rows),
            "target_data": _json_text(sample_rows),
            "dimension_data": _json_text(sample_rows),
            "base_data": _json_text(base_data),
            "compare_data": _json_text(compare_data),
            "row_count": row_count,
            "column_count": column_count,
            "columns": _json_text(columns),
            "null_stats": _json_text(null_stats),
            "statistics": _json_text({"numeric_columns": numeric_stats}),
            "data_statistics": _json_text({"numeric_columns": numeric_stats}),
            "mean": mean(numeric_values) if numeric_values else 0,
            "median": median(numeric_values) if numeric_values else 0,
            "std": pstdev(numeric_values) if len(numeric_values) > 1 else 0,
            "min_val": min(numeric_values) if numeric_values else 0,
            "max_val": max(numeric_values) if numeric_values else 0,
            "variables": _json_text(columns),
            "time_column": time_col,
            "value_column": value_col,
            "field_name": value_col or (columns[0] if columns else ""),
            "field_type": "numeric" if value_col in numeric_columns else "string",
            "analysis_result": _json_text(analysis_result),
            "insights": _json_text(insight_text),
            "chart_info": _json_text(chart_info),
            "chart_configs": _json_text([state.get("chart_config", {})] if state.get("chart_config") else []),
            "key_metrics": _json_text(state.get("calculated_metrics", {})),
            "metrics_to_calculate": _json_text(state.get("metric_entities", [])),
            "time_range": time_range,
            "forecast_horizon": "未来30天",
            "target_metric": target_metric,
            "kpi_definitions": _json_text(state.get("metric_definitions", [])),
            "period": time_range,
            "anomalies": _json_text(state.get("anomalies", [])),
            "business_context": str(_first_non_empty(state.get("user_message"), "")),
            "data_summary": _json_text({"row_count": row_count, "column_count": column_count}),
            "analysis_purpose": str(_first_non_empty(state.get("query_type"), "general_analysis")),
            "category_counts": _json_text({"categories": column_count}),
            "column_types": _json_text({col: ("numeric" if col in numeric_columns else "string") for col in columns}),
            "comparison_type": str(_first_non_empty(state.get("comparison_type"), state.get("query_type"), "comparison")),
            "base_value": base_value,
            "current_value": current_value,
            "change_rate": change_rate,
            "file_name": os.path.basename(file_path) if file_path else "",
            "file_size": len(file_content),
            "file_content_preview": file_content[:1000],
            "parsed_file": _json_text(parsed_file),
            "data_preview": _json_text(sample_rows_20),
        }
    )
    return ctx


def safe_format_prompt(template: str, **kwargs) -> str:
    """Format prompt templates with semantic fallback values."""
    state = kwargs.pop("_state", None)
    if not isinstance(state, Mapping):
        state = _infer_state_from_caller()

    context = dict(kwargs)
    if isinstance(state, Mapping):
        common = _build_common_context(state, context)
        for k, v in common.items():
            context.setdefault(k, v)

    # Alias normalization for historical naming differences.
    if "generated_sql" in context:
        context.setdefault("sql", context["generated_sql"])
        context.setdefault("original_sql", context["generated_sql"])
    if "matched_tables" in context:
        context.setdefault("schema_context", context["matched_tables"])
    if "recommendations" in context and "insights" not in context:
        context["insights"] = context["recommendations"]

    return template.format_map(_SafeFormatDict(context))
