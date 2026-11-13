from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

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
    
    class Config:
        from_attributes = True

class SellerResponse(BaseModel):
    availability_type: str
    action: str

class SignDeal(BaseModel):
    final_minor: int
    dispatch_mode: str
