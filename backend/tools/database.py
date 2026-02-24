"""数据库连接与查询工具"""

from typing import Any
from config import settings

# 数据库引擎缓存
_engines: dict[str, Any] = {}


def _get_sqlalchemy():
    """延迟导入 SQLAlchemy，避免在应用启动导入阶段触发平台探测问题。"""
    from sqlalchemy import create_engine, text, inspect
    return create_engine, text, inspect


def get_engine(dataset_id: str | None = None, db_url: str | None = None):
    """获取数据库引擎（带缓存）"""
    create_engine, _, _ = _get_sqlalchemy()
    url = db_url or settings.default_db_url
    cache_key = dataset_id or url

    if cache_key not in _engines:
        _engines[cache_key] = create_engine(url, echo=settings.sql_echo)

    return _engines[cache_key]


def execute_query(sql: str, dataset_id: str | None = None, db_url: str | None = None) -> dict:
    """执行 SQL 查询，返回结果"""
    _, text, _ = _get_sqlalchemy()
    engine = get_engine(dataset_id, db_url)

    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

    return {"columns": columns, "data": rows}


def get_table_names(dataset_id: str | None = None, db_url: str | None = None) -> list[str]:
    """获取数据库中所有表名"""
    _, _, inspect = _get_sqlalchemy()
    engine = get_engine(dataset_id, db_url)
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_table_schema(table_name: str, dataset_id: str | None = None, db_url: str | None = None) -> dict:
    """获取单张表的完整 Schema 信息"""
    _, _, inspect = _get_sqlalchemy()
    engine = get_engine(dataset_id, db_url)
    inspector = inspect(engine)

    columns = []
    for col in inspector.get_columns(table_name):
        columns.append({
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col.get("nullable", True),
            "default": str(col.get("default", "")) if col.get("default") else None,
            "comment": col.get("comment", ""),
        })

    primary_keys = inspector.get_pk_constraint(table_name)
    foreign_keys = inspector.get_foreign_keys(table_name)

    return {
        "name": table_name,
        "columns": columns,
        "primary_keys": primary_keys.get("constrained_columns", []),
        "foreign_keys": [
            {
                "columns": fk["constrained_columns"],
                "referred_table": fk["referred_table"],
                "referred_columns": fk["referred_columns"],
            }
            for fk in foreign_keys
        ],
        "comment": inspector.get_table_comment(table_name).get("text", ""),
    }


def get_full_schema(dataset_id: str | None = None, db_url: str | None = None) -> dict:
    """获取数据库的完整 Schema（所有表）"""
    table_names = get_table_names(dataset_id, db_url)
    tables = [get_table_schema(name, dataset_id, db_url) for name in table_names]
    return {"tables": tables}
