from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class DroppCreate(BaseModel):
    source_url: str
    source_platform: str
    title: str
    currency: str
    offer_minor: int
    image_url: Optional[str] = None

class DroppResponse(BaseModel):
    id: UUID
    code: str
    buyer_id: str
    seller_id: Optional[str]
    title: str
    status: str
    currency: str
    offer_minor: int
    final_minor: Optional[int]
    availability_type: Optional[str]
    dispatch_mode: Optional[str]
    buyer_signature: Optional[str]
    seller_signature: Optional[str]
    checkout_token: Optional[str]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    auto_release_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SellerResponse(BaseModel):
    availability_type: str
    action: str

class SignDeal(BaseModel):
    final_minor: int
    dispatch_mode: str
