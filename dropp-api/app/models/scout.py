from sqlalchemy import Column, String, BigInteger
from app.models.base import BaseModel

class WantedRequest(BaseModel):
    __tablename__ = "wanted_requests"
    
    buyer_id = Column(String, index=True, nullable=False)
    item_description = Column(String, nullable=False)
    target_price_minor = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="searching", nullable=False) # searching, matched, fulfilled
