"""数据分析 Node — 对查询结果进行深入分析"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.analyzer import ANALYZER_SYSTEM_PROMPT, ANALYZER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def analyzer_node(state: AgentState) -> dict:
    """对 SQL 查询结果进行深入分析，提炼数据洞察"""

    user_message = state.get("user_message", "")
    generated_sql = state.get("generated_sql", "")
    sql_result = state.get("sql_result", [])
    sql_result_columns = state.get("sql_result_columns", [])

    step = {
        "node_name": "analyzer",
        "status": NodeStatus.RUNNING.value,
        "title": "数据分析",
        "detail": "正在分析查询结果...",
        "data": {},
    }

    data_preview = sql_result[:50]
    data_str = json.dumps(data_preview, ensure_ascii=False, indent=2)
    columns_str = json.dumps(sql_result_columns, ensure_ascii=False)

    llm = get_llm()
    prompt = safe_format_prompt(ANALYZER_USER_PROMPT, 
        user_message=user_message,
        generated_sql=generated_sql,
        columns=columns_str,
        data=data_str,
    )

    response = llm.invoke([
        {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ])

    result: dict | None = None
    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        # 尝试从 markdown 代码块中提取 JSON
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response.content, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                result = None

        # 尝试直接提取首个 JSON 对象（非 markdown 包裹）
        if result is None:
            object_match = re.search(r'(\{[\s\S]*\})', response.content)
            if object_match:
                try:
                    result = json.loads(object_match.group(1))
                except json.JSONDecodeError:
                    result = None

    if not isinstance(result, dict):
        result = {
            "summary": response.content[:200],
            "key_metrics": {},
            "trends": [],
            "anomalies": [],
            "insights": [response.content[:300]],
            "recommendations": [],
        }

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"分析完成：{result.get('summary', '')[:80]}"
    step["data"] = {
        "summary": result.get("summary", ""),
        "key_metrics": result.get("key_metrics", {}),
        "insight_count": len(result.get("insights", [])),
    }

    return {
        "analysis_result": result,
        "report_insights": result.get("insights", []),
        "steps": [step],
    }
