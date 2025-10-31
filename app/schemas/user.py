from typing import List, Optional
from pydantic import BaseModel, EmailStr
from .bookmark import BookmarkResponse 

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    bookmarks: List[BookmarkResponse] = []
    username: Optional[str] = None 
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse