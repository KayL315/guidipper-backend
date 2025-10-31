from pydantic import BaseModel
from typing import Optional

class BookmarkBase(BaseModel):
    title: str
    address: str
    latitude: float
    longitude: float
    category: Optional[str] = None
    google_maps_url: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    pass

class BookmarkResponse(BookmarkBase):
    id: int

    class Config:
        orm_mode = True