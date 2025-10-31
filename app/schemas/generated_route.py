# schemas/generated_route.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GeneratedRouteCreate(BaseModel):
    route_text: str

class GeneratedRouteResponse(BaseModel):
    id: int
    user_id: int
    route_text: str
    created_at: datetime

    class Config:
        orm_mode = True