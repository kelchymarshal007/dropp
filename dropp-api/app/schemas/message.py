from pydantic import BaseModel
from datetime import datetime

class MessageIn(BaseModel):
    body: str

class MessageOut(BaseModel):
    id: str
    dropp_id: str
    sender_type: str # buyer, seller, agent
    sender_id: str
    body: str
    created_at: datetime
