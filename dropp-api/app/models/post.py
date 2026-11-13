from sqlalchemy import Column, String, BigInteger, Integer
from app.models.base import BaseModel

class Post(BaseModel):
    __tablename__ = "posts"
    
    seller_id = Column(String, index=True, nullable=False)
    media_url = Column(String, nullable=True) # The .m3u8 HLS URL
    media_type = Column(String(10), nullable=False) # video or image
    caption = Column(String, nullable=True)
    
    price_minor = Column(BigInteger, nullable=True)
    currency = Column(String(3), nullable=True)
    
    status = Column(String, default="pending_upload", nullable=False, index=True)
    
    # Social Counters
    like_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    dropp_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
