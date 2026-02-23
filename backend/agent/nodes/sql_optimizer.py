"""SQL 优化 Node — 优化 SQL 查询性能"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.sql_optimizer import SQL_OPTIMIZER_SYSTEM_PROMPT, SQL_OPTIMIZER_USER_PROMPT
from agent.llm import get_llm


def sql_optimizer_node(state: AgentState) -> dict:
    """优化 SQL 查询，提升执行性能"""

    generated_sql = state.get("generated_sql", "")
    matched_tables = state.get("matched_tables", [])

    step = {
        "node_name": "sql_optimizer",
        "status": NodeStatus.RUNNING.value,
        "title": "SQL 优化",
        "detail": "正在优化 SQL 查询...",
        "data": {},
    }

    llm = get_llm()
    prompt = SQL_OPTIMIZER_USER_PROMPT.format(
        generated_sql=generated_sql,
        matched_tables=json.dumps(matched_tables, ensure_ascii=False),
    )

    response = llm.invoke([
        {"role": "system", "content": SQL_OPTIMIZER_SYSTEM_PROMPT},
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
            "optimized_sql": generated_sql,
            "optimizations_applied": [],
            "performance_notes": [],
        }

    optimized_sql = result.get("optimized_sql", generated_sql)
    optimizations = result.get("optimizations_applied", [])

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"应用了 {len(optimizations)} 项优化"
    step["data"] = {
        "optimizations_count": len(optimizations),
        "optimizations": optimizations,
    }

    return {
        "generated_sql": optimized_sql,
        "sql_optimizations": optimizations,
        "sql_performance_notes": result.get("performance_notes", []),
        "steps": [step],
    }
