from sqlalchemy import Column, String, Text
from app.models.base import BaseModel

class PostLike(BaseModel):
    __tablename__ = "post_likes"
    post_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)

class PostComment(BaseModel):
    __tablename__ = "post_comments"
    post_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    parent_id = Column(String, nullable=True)
    body = Column(Text, nullable=False)
