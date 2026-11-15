from sqlalchemy import Column, String, BigInteger, Integer
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import BaseModel

class Post(BaseModel):
    __tablename__ = "posts"
    
    seller_id = Column(String, index=True, nullable=False)
    # JSONB allows us to store an array of URLs ["url1.jpg", "url2.jpg"]
    media_urls = Column(JSONB, nullable=False, default=list) 
    media_type = Column(String(10), nullable=False) # video or carousel
    
    caption = Column(String, nullable=True)
    price_minor = Column(BigInteger, nullable=True)
    currency = Column(String(3), nullable=True)
    category = Column(String, nullable=True)
    subcategory = Column(String, nullable=True)
    
    status = Column(String, default="active", nullable=False, index=True)
    
    like_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    dropp_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
