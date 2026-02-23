"""Schema 检索 Node — 从元数据中找到与用户问题相关的表和字段"""

from agent.state import AgentState, NodeStatus
from data.datasets.manager import dataset_manager


def schema_search_node(state: AgentState) -> dict:
    """检索数据集中与用户问题相关的表结构信息"""

    dataset_id = state.get("dataset_id") or "demo_ecommerce"

    step = {
        "node_name": "schema_search",
        "status": NodeStatus.RUNNING.value,
        "title": "检索数据表",
        "detail": "正在匹配相关数据表...",
        "data": {},
    }

    schema = dataset_manager.get_schema(dataset_id)

    if not schema:
        step["status"] = NodeStatus.FAILED.value
        step["detail"] = "未找到可用的数据集"
        return {
            "dataset_id": dataset_id,
            "error": "未找到可用的数据集，请先创建或选择一个数据集",
            "steps": [step],
        }

    schema_lines = []
    matched_tables = []

    for table in schema.get("tables", []):
        table_name = table["name"]
        table_comment = table.get("comment", "")
        columns_desc = []
        for col in table.get("columns", []):
            col_desc = f"  - {col['name']} ({col['type']})"
            if col.get("comment"):
                col_desc += f"  -- {col['comment']}"
            columns_desc.append(col_desc)

        table_block = f"表名: {table_name}"
        if table_comment:
            table_block += f" ({table_comment})"
        table_block += "\n字段:\n" + "\n".join(columns_desc)
        schema_lines.append(table_block)

        matched_tables.append({
            "name": table_name,
            "comment": table_comment,
            "column_count": len(table.get("columns", [])),
        })

    schema_context = "\n\n".join(schema_lines)

    table_names = [t["name"] for t in matched_tables]
    step["status"] = NodeStatus.SUCCESS.value
    step["detail"] = f"已匹配到 {len(matched_tables)} 张表：{', '.join(table_names)}"
    step["data"] = {"tables": matched_tables}

    return {
        "dataset_id": dataset_id,
        "schema_context": schema_context,
        "matched_tables": matched_tables,
        "steps": [step],
    }