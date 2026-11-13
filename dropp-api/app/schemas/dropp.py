from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class DroppCreate(BaseModel):
    buyer_id: str = Field(..., description="The ID of the buyer creating the Dropp")
    source_url: str = Field(..., description="The Instagram/TikTok link")
    source_platform: str = Field(..., description="instagram, tiktok, whatsapp")
    title: str = Field(..., description="Name of the item")
    currency: str = Field(..., description="Currency code (NGN, KES, USD) - NO HARDCODING")
    offer_minor: int = Field(..., description="Offer amount in minor units (kobo/cents)")
    image_url: Optional[str] = None

class DroppResponse(BaseModel):
    id: UUID
    code: str
    buyer_id: str
    seller_id: Optional[str] = None
    title: str
    status: str
    currency: str
    offer_minor: int
    
    class Config:
        from_attributes = True
