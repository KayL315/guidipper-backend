# app/models/user.py

from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)

    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete")
    generated_routes = relationship("GeneratedRoute", back_populates="user")