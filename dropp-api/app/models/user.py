from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    handle = Column(String, unique=True, index=True, nullable=True)
    phone_e164 = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    # Roles: user, admin, support
    role = Column(String, default="user", nullable=False)
    phone_verified = Column(Boolean, default=False, nullable=False)
    country = Column(String(2), nullable=True)
