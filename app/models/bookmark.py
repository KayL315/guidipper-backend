# app/models/bookmark.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    category = Column(String)
    google_maps_url = Column(String)

    user = relationship("User", back_populates="bookmarks")