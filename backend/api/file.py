"""文件上传与管理 API"""

import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File
import aiofiles

from config import settings

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件（Excel/CSV/PDF），返回文件 ID 和解析结果摘要"""

    file_id = str(uuid.uuid4())
    suffix = Path(file.filename).suffix.lower()
    save_path = Path(settings.upload_dir) / f"{file_id}{suffix}"

    async with aiofiles.open(save_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    # 根据文件类型解析
    from tools.file_reader import parse_uploaded_file
    parse_result = parse_uploaded_file(str(save_path), suffix)

    return {
        "file_id": file_id,
        "filename": file.filename,
        "file_type": suffix,
        "save_path": str(save_path),
        "parse_result": parse_result,
    }


@router.get("/list")
async def list_uploaded_files():
    """列出已上传的文件"""
    upload_dir = Path(settings.upload_dir)
    files = []
    if upload_dir.exists():
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "path": str(file_path),
                })
    return {"files": files}
