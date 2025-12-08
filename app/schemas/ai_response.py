from pydantic import BaseModel
from typing import Optional

class AIResponse(BaseModel):
    chat_message: str
    diff: Optional[str] = None
