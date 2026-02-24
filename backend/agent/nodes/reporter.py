"""报告组装 Node — 将分析结果组装成完整报告并导出多种格式"""

import json
import re
import uuid
from pathlib import Path

from agent.state import AgentState, IntentType, NodeStatus
from agent.prompts.reporter import REPORTER_SYSTEM_PROMPT, REPORTER_USER_PROMPT
from agent.llm import get_llm
from tools.file_writer import (
    generate_html_report,
    generate_excel_export,
    generate_ppt_export,
)
from config import settings
from agent.prompt_utils import safe_format_prompt


def reporter_node(state: AgentState) -> dict:
    """将数据分析结果、图表、洞察组装成完整报告"""

    user_message = state.get("user_message", "")
    intent = state.get("intent", "data_query")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])
    analysis_result = state.get("analysis_result", {})
    chart_config = state.get("chart_config", {})
    existing_insights = state.get("report_insights", [])

    step = {
        "node_name": "reporter",
        "status": NodeStatus.RUNNING.value,
        "title": "生成报告",
        "detail": "正在组装分析报告...",
        "data": {},
    }

    data_summary = f"共 {len(sql_result)} 行数据，字段：{', '.join(sql_result_columns)}"
    analysis_str = json.dumps(analysis_result, ensure_ascii=False, indent=2)
    chart_str = json.dumps(chart_config, ensure_ascii=False, indent=2)

    llm = get_llm()
    prompt = safe_format_prompt(REPORTER_USER_PROMPT, 
        user_message=user_message,
        intent=intent,
        analysis_result=analysis_str,
        chart_config=chart_str,
        columns=json.dumps(sql_result_columns, ensure_ascii=False),
        data_summary=data_summary,
    )

    response = llm.invoke([
        {"role": "system", "content": REPORTER_SYSTEM_PROMPT},
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
            result = {
                "title": "数据分析报告",
                "summary": response.content[:300],
                "sections": [],
                "insights": existing_insights,
                "recommendations": [],
                "markdown_report": response.content,
            }

    report_title = result.get("title", "数据分析报告")
    report_summary = result.get("summary", "")
    report_insights = result.get("insights", existing_insights)
    report_markdown = result.get("markdown_report", "")

    report_id = str(uuid.uuid4())[:8]
    export_dir = Path(settings.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    html_filename = f"report_{report_id}.html"
    report_html = generate_html_report(
        title=report_title,
        summary=report_summary,
        sections=result.get("sections", []),
        insights=report_insights,
        recommendations=result.get("recommendations", []),
        chart_config=chart_config,
        output_path=str(export_dir / html_filename),
    )

    excel_filename = f"data_{report_id}.xlsx"
    excel_path = generate_excel_export(
        data=sql_result,
        columns=sql_result_columns,
        analysis=analysis_result,
        output_path=str(export_dir / excel_filename),
    )

    ppt_path = ""
    ppt_filename = ""
    if intent in (IntentType.REPORT.value, IntentType.DASHBOARD.value):
        ppt_filename = f"report_{report_id}.pptx"
        ppt_path = generate_ppt_export(
            title=report_title,
            summary=report_summary,
            insights=report_insights,
            recommendations=result.get("recommendations", []),
            output_path=str(export_dir / ppt_filename),
        )

    final_answer = _build_final_answer(
        report_title, report_summary, report_insights, ppt_path
    )

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"报告已生成：{report_title}"
    step["data"] = {
        "report_title": report_title,
        "html_url": f"/exports/{html_filename}",
        "excel_url": f"/exports/{excel_filename}",
        "ppt_url": f"/exports/{ppt_filename}" if ppt_path else "",
    }

    return {
        "report_title": report_title,
        "report_summary": report_summary,
        "report_insights": report_insights,
        "report_html": report_html,
        "report_markdown": report_markdown,
        "excel_path": excel_path,
        "ppt_path": ppt_path,
        "final_answer": final_answer,
        "steps": [step],
    }


def _build_final_answer(
    report_title: str,
    report_summary: str,
    report_insights: list[str],
    ppt_path: str,
) -> str:
    """组装最终的文字回答"""
    parts = []

    parts.append(f"## {report_title}\n")
    parts.append(f"{report_summary}\n")

    if report_insights:
        parts.append("### 关键洞察\n")
        for idx, insight in enumerate(report_insights, 1):
            parts.append(f"{idx}. {insight}")
        parts.append("")

    parts.append("### 导出文件\n")
    parts.append("- 📊 HTML 报告已生成")
    parts.append("- 📋 Excel 数据已导出")
    if ppt_path:
        parts.append("- 📑 PPT 演示文稿已生成")

    return "\n".join(parts)