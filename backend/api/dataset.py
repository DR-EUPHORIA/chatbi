"""数据集管理 API"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class DatasetCreateRequest(BaseModel):
    """创建数据集请求"""
    name: str
    db_type: str = "sqlite"
    db_url: str = ""
    description: str = ""


class DatasetInfo(BaseModel):
    """数据集信息"""
    dataset_id: str
    name: str
    db_type: str
    tables: list[str] = []
    description: str = ""


@router.get("/list")
async def list_datasets():
    """获取所有数据集"""
    from data.datasets.manager import dataset_manager
    datasets = dataset_manager.list_datasets()
    return {"datasets": datasets}


@router.post("/create")
async def create_dataset(request: DatasetCreateRequest):
    """创建新数据集"""
    from data.datasets.manager import dataset_manager
    dataset = dataset_manager.create_dataset(
        name=request.name,
        db_type=request.db_type,
        db_url=request.db_url,
        description=request.description,
    )
    return {"dataset": dataset}


@router.get("/{dataset_id}/schema")
async def get_dataset_schema(dataset_id: str):
    """获取数据集的表结构信息"""
    from data.datasets.manager import dataset_manager
    schema = dataset_manager.get_schema(dataset_id)
    return {"schema": schema}


@router.post("/init-demo")
async def init_demo_database():
    """初始化 Demo 电商数据库（创建表并填充模拟数据）"""
    from data.demo.init_db import init_demo_db
    try:
        result = init_demo_db()
        return {"status": "ok", "message": result}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """删除数据集"""
    from data.datasets.manager import dataset_manager
    dataset_manager.delete_dataset(dataset_id)
    return {"status": "ok"}
