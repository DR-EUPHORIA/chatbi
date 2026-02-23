"""SQL 执行 Node — 执行生成的 SQL 并返回结果"""

from agent.state import AgentState, NodeStatus
from tools.database import execute_query


def sql_executor_node(state: AgentState) -> dict:
    """执行 SQL 查询并获取结果"""

    generated_sql = state.get("generated_sql", "")
    dataset_id = state.get("dataset_id")
    retry_count = state.get("sql_retry_count", 0)

    step = {
        "node_name": "sql_executor",
        "status": NodeStatus.RUNNING.value,
        "title": "执行查询",
        "detail": f"正在执行 SQL（第 {retry_count + 1} 次）...",
        "data": {},
    }

    if not generated_sql:
        step["status"] = NodeStatus.FAILED.value
        step["detail"] = "没有可执行的 SQL"
        return {"error": "没有可执行的 SQL", "steps": [step]}

    try:
        result = execute_query(sql=generated_sql, dataset_id=dataset_id)
        sql_result = result["data"]
        sql_result_columns = result["columns"]
        row_count = len(sql_result)

        step["status"] = NodeStatus.SUCCESS.value
        step["detail"] = f"查询成功，返回 {row_count} 行数据"
        step["data"] = {
            "row_count": row_count,
            "columns": sql_result_columns,
            "preview": sql_result[:5],
        }

        return {
            "sql_result": sql_result,
            "sql_result_columns": sql_result_columns,
            "sql_error": "",
            "steps": [step],
        }

    except Exception as exc:
        sql_error = str(exc)
        step["status"] = NodeStatus.FAILED.value
        step["detail"] = f"SQL 执行失败：{sql_error}"
        step["data"] = {"error": sql_error, "retry_count": retry_count + 1}

        return {
            "sql_error": sql_error,
            "sql_retry_count": retry_count + 1,
            "steps": [step],
        }