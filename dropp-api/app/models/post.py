from sqlalchemy import Column, String, BigInteger
from app.models.base import BaseModel

class Post(BaseModel):
    __tablename__ = "posts"
    
    seller_id = Column(String, index=True, nullable=False)
    media_url = Column(String, nullable=False)
    media_type = Column(String(10), nullable=False) # video or image
    caption = Column(String, nullable=True)
    
    # Price is optional (for quick drops)
    price_minor = Column(BigInteger, nullable=True)
    currency = Column(String(3), nullable=False) 
    
    status = Column(String, default="active", nullable=False)
