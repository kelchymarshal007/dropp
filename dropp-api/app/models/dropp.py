from sqlalchemy import Column, String, BigInteger, Integer
from app.models.base import BaseModel

class Dropp(BaseModel):
    __tablename__ = "dropps"
    
    code = Column(String(10), unique=True, index=True, nullable=False)
    buyer_id = Column(String, index=True, nullable=False)
    seller_id = Column(String, index=True, nullable=True)
    
    source_url = Column(String, nullable=False)
    source_platform = Column(String, nullable=False) # instagram, tiktok, whatsapp
    
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    # NO HARDCODED CURRENCIES. Comes from payload.
    currency = Column(String(3), nullable=False) 
    
    # Money in minor units (kobo, cents)
    offer_minor = Column(BigInteger, nullable=False)
    final_minor = Column(BigInteger, nullable=True)
    fee_minor = Column(BigInteger, nullable=True)
    
    status = Column(String, default="draft", nullable=False, index=True)
    version = Column(Integer, default=0, nullable=False) # For optimistic locking
