from sqlalchemy import Column, String
from app.models.base import BaseModel

class Follow(BaseModel):
    __tablename__ = "follows"
    
    follower_id = Column(String, index=True, nullable=False)
    following_id = Column(String, index=True, nullable=False)
