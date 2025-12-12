from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatSessionCreate(BaseModel):
    generated_route_id: Optional[int] = None
    route_text: Optional[str] = None


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    generated_route_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ChatSessionWithRoute(ChatSessionResponse):
    route_text: Optional[str] = None
