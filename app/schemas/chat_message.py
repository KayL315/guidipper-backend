from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageCreate(BaseModel):
    content: str
    route_text: Optional[str] = None  # 当前计划文本，用于未保存情况下聊天上下文


class ChatMessageResponse(BaseModel):
    id: int
    chat_session_id: int
    role: str
    content: str
    diff_content: Optional[str] = None
    chat_message: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
