"""ChatBI Mini — FastAPI 入口"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import settings
from api.chat import router as chat_router
from api.dataset import router as dataset_router
from api.file import router as file_router
from api.export import router as export_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="对话式智能数据分析平台",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 静态文件（导出的报告等）──
export_path = Path(settings.export_dir)
export_path.mkdir(parents=True, exist_ok=True)
app.mount("/exports", StaticFiles(directory=str(export_path)), name="exports")

upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)

# ── 路由注册 ──
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(dataset_router, prefix="/api/dataset", tags=["Dataset"])
app.include_router(file_router, prefix="/api/file", tags=["File"])
app.include_router(export_router, prefix="/api/export", tags=["Export"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
