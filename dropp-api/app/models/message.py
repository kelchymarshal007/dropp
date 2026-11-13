from sqlalchemy import Column, String
from app.models.base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"
    
    dropp_id = Column(String, index=True, nullable=False)
    sender_type = Column(String, nullable=False) # buyer, seller, agent
    sender_id = Column(String, nullable=True)
    body = Column(String, nullable=False)
