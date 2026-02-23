"""报告导出 API"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ExportRequest(BaseModel):
    """导出请求"""
    session_id: str
    format: str  # html / markdown / excel / ppt
    content: dict = {}


@router.post("/generate")
async def generate_export(request: ExportRequest):
    """根据对话结果生成导出文件"""
    from tools.file_writer import generate_export_file
    result = generate_export_file(
        session_id=request.session_id,
        export_format=request.format,
        content=request.content,
    )
    return result


@router.get("/list")
async def list_exports():
    """列出已生成的导出文件"""
    from pathlib import Path
    from config import settings

    export_dir = Path(settings.export_dir)
    files = []
    if export_dir.exists():
        for file_path in export_dir.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "url": f"/exports/{file_path.name}",
                })
    return {"files": files}
