"""数据集管理器 — 管理多个数据集的元数据和连接"""

import uuid
from typing import Any

from tools.database import get_full_schema, get_engine
from config import settings


class DatasetManager:
    """数据集管理器（内存存储版本）"""

    def __init__(self):
        self._datasets: dict[str, dict[str, Any]] = {}
        self._schema_cache: dict[str, dict] = {}
        self._init_demo_datasets()

    def _init_demo_datasets(self):
        """初始化预置的 Demo 数据集"""
        self._datasets["demo_ecommerce"] = {
            "dataset_id": "demo_ecommerce",
            "name": "电商销售数据（Demo）",
            "db_type": "sqlite",
            "db_url": settings.default_db_url,
            "description": "包含订单、商品、品类、用户等电商核心数据，约 10 万条模拟数据",
        }

    def list_datasets(self) -> list[dict[str, Any]]:
        """列出所有数据集"""
        return list(self._datasets.values())

    def create_dataset(self, name: str, db_type: str, db_url: str, description: str = "") -> dict[str, Any]:
        """创建新数据集"""
        dataset_id = str(uuid.uuid4())[:8]
        dataset = {
            "dataset_id": dataset_id,
            "name": name,
            "db_type": db_type,
            "db_url": db_url,
            "description": description,
        }
        self._datasets[dataset_id] = dataset

        # 清除 schema 缓存
        if dataset_id in self._schema_cache:
            del self._schema_cache[dataset_id]

        return dataset

    def get_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        """获取数据集信息"""
        return self._datasets.get(dataset_id)

    def delete_dataset(self, dataset_id: str) -> None:
        """删除数据集"""
        self._datasets.pop(dataset_id, None)
        self._schema_cache.pop(dataset_id, None)

    def get_schema(self, dataset_id: str) -> dict | None:
        """获取数据集的表结构信息（带缓存）"""
        if dataset_id in self._schema_cache:
            return self._schema_cache[dataset_id]

        dataset = self._datasets.get(dataset_id)
        if not dataset:
            return None

        try:
            schema = get_full_schema(dataset_id=dataset_id, db_url=dataset["db_url"])
            self._schema_cache[dataset_id] = schema
            return schema
        except Exception as exc:
            return {"tables": [], "error": str(exc)}

    def get_db_url(self, dataset_id: str) -> str | None:
        """获取数据集的数据库连接 URL"""
        dataset = self._datasets.get(dataset_id)
        if dataset:
            return dataset["db_url"]
        return None


# 全局单例
dataset_manager = DatasetManager()
