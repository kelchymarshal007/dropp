from sqlalchemy import Column, String
from app.models.base import BaseModel

class Bookmark(BaseModel):
    __tablename__ = "bookmarks"
    user_id = Column(String, index=True, nullable=False)
    item_id = Column(String, index=True, nullable=False)
    item_type = Column(String, nullable=False, default="post") # 'post' or 'comment'
