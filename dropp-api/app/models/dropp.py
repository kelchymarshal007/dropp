from sqlalchemy import Column, String, BigInteger, Integer, DateTime
from app.models.base import BaseModel

class Dropp(BaseModel):
    __tablename__ = "dropps"
    
    code = Column(String(10), unique=True, index=True, nullable=False)
    buyer_id = Column(String, index=True, nullable=False)
    seller_id = Column(String, index=True, nullable=True)
    
    source_url = Column(String, nullable=False)
    source_platform = Column(String, nullable=False)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    currency = Column(String(3), nullable=False) 
    
    offer_minor = Column(BigInteger, nullable=False)
    final_minor = Column(BigInteger, nullable=True)
    fee_minor = Column(BigInteger, nullable=True)
    
    availability_type = Column(String, nullable=True) 
    dispatch_mode = Column(String, nullable=True) 
    buyer_signature = Column(String, nullable=True) 
    seller_signature = Column(String, nullable=True) 
    checkout_token = Column(String, nullable=True, unique=True) 
    
    # Timers for the "Smart Escrow"
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    auto_release_at = Column(DateTime(timezone=True), nullable=True) # 24 hours after delivery
    
    status = Column(String, default="draft", nullable=False, index=True)
    version = Column(Integer, default=0, nullable=False)
