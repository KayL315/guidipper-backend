from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class GeneratedRoute(Base):
    __tablename__ = "generated_routes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    route_text = Column(Text, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="generated_routes")