"""对话 API — SSE 流式推送 Agent 执行过程"""

import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agent.graph import run_agent_stream

router = APIRouter()


class ChatMessageRequest(BaseModel):
    """前端发送的对话请求"""
    message: str
    session_id: str | None = None
    dataset_id: str | None = None
    model: str | None = None


@router.post("/stream")
async def chat_stream(request: ChatMessageRequest):
    """SSE 流式对话接口，实时推送 Agent 每一步的执行状态"""

    session_id = request.session_id or str(uuid.uuid4())

    async def event_generator() -> AsyncGenerator[dict, None]:
        async for event in run_agent_stream(
            message=request.message,
            session_id=session_id,
            dataset_id=request.dataset_id,
        ):
            yield {
                "event": event["type"],
                "data": json.dumps(event["data"], ensure_ascii=False),
            }

    return EventSourceResponse(event_generator())


@router.get("/sessions")
async def list_sessions():
    """获取历史会话列表（内存存储）"""
    return {"sessions": []}
