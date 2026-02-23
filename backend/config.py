"""ChatBI Mini 全局配置"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置，优先从环境变量 / .env 文件读取"""

    # ── 应用 ──
    app_name: str = "ChatBI Mini"
    app_version: str = "0.1.0"
    debug: bool = True

    # ── LLM ──
    llm_provider: str = "openai"  # openai / azure / dashscope
    openai_api_key: str = ""
    openai_api_base: Optional[str] = None
    openai_model: str = "gpt-4o"
    temperature: float = 0.0

    # ── 数据库（Demo 默认使用 SQLite）──
    default_db_type: str = "sqlite"
    default_db_url: str = "sqlite:///data/demo/ecommerce.db"

    # ── 文件存储 ──
    upload_dir: str = "uploads"
    export_dir: str = "exports"

    # ── 向量库 ──
    vector_store_type: str = "faiss"  # faiss / chroma
    vector_store_path: str = "data/vector_store"

    # ── 服务 ──
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
