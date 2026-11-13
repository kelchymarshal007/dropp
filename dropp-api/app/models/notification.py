from sqlalchemy import Column, String, Boolean, Text
from app.models.base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"
    
    user_id = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False) # scout_match, escrow_update, chat, system
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    channel = Column(String, default="in_app", nullable=False) # in_app, email, sms, push
    is_read = Column(Boolean, default=False, nullable=False)
