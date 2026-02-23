"""LLM 实例工厂 — 独立模块，避免循环导入"""

from langchain_openai import ChatOpenAI
from config import settings


def get_llm(model: str | None = None) -> ChatOpenAI:
    """根据配置获取 LLM 实例"""
    return ChatOpenAI(
        model=model or settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        temperature=settings.temperature,
    )
