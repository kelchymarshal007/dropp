from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, String, Text, Integer
from app.models.base import BaseModel

class PostLike(BaseModel):
    __tablename__ = "post_likes"
    post_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)

class PostComment(BaseModel):
    __tablename__ = "post_comments"
    post_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    parent_id = Column(String, nullable=True) # If set, this is a reply
    body = Column(Text, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    media_urls = Column(JSONB, default=list)

class CommentLike(BaseModel):
    __tablename__ = "comment_likes"
    comment_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
