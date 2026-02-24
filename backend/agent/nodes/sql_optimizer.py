"""SQL 优化 Node — 优化 SQL 查询性能"""

import json
import re
from agent.state import AgentState, NodeStatus
from agent.prompts.sql_optimizer import SQL_OPTIMIZER_SYSTEM_PROMPT, SQL_OPTIMIZER_USER_PROMPT
from agent.llm import get_llm
from agent.prompt_utils import safe_format_prompt


def sql_optimizer_node(state: AgentState) -> dict:
    """优化 SQL 查询，提升执行性能"""

    generated_sql = state.get("generated_sql", "")
    matched_tables = state.get("matched_tables", [])
    schema_context = state.get("schema_context", "")

    step = {
        "node_name": "sql_optimizer",
        "status": NodeStatus.RUNNING.value,
        "title": "SQL 优化",
        "detail": "正在优化 SQL 查询...",
        "data": {},
    }

    schema_text = schema_context if schema_context else json.dumps(matched_tables, ensure_ascii=False)
    if not schema_text:
        schema_text = "暂无表结构信息"

    llm = get_llm()
    prompt = safe_format_prompt(SQL_OPTIMIZER_USER_PROMPT, 
        original_sql=generated_sql,
        schema_context=schema_text,
        dialect="sqlite",
        table_stats="暂无表统计信息",
        # 兼容历史 Prompt 占位符命名
        generated_sql=generated_sql,
        matched_tables=schema_text,
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
    if not isinstance(optimizations, list):
        optimizations = []

    performance_notes = result.get("performance_notes")
    if not isinstance(performance_notes, list):
        performance_notes = []
        estimate = result.get("performance_estimate")
        if isinstance(estimate, dict) and estimate:
            performance_notes.append(json.dumps(estimate, ensure_ascii=False))
        warnings = result.get("warnings")
        if isinstance(warnings, list):
            performance_notes.extend([str(w) for w in warnings])

    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"应用了 {len(optimizations)} 项优化"
    step["data"] = {
        "optimizations_count": len(optimizations),
        "optimizations": optimizations,
    }

    return {
        "generated_sql": optimized_sql,
        "sql_optimizations": optimizations,
        "sql_performance_notes": performance_notes,
        "steps": [step],
    }
