from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    # Identity
    handle = Column(String, unique=True, index=True, nullable=True) # @username
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Auth Methods (All nullable to support different signup flows)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True) # Only for email signups
    phone_e164 = Column(String, unique=True, index=True, nullable=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    apple_id = Column(String, unique=True, index=True, nullable=True)
    
    # State
    is_seller = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(String, default="user", nullable=False) # user, admin
