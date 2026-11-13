from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class WantedRequestCreate(BaseModel):
    item_description: str = Field(..., min_length=3)
    target_price_minor: int = Field(..., gt=0)
    currency: str = Field(...)
    location: str = Field(..., min_length=2)


class WantedRequestResponse(BaseModel):
    id: UUID
    buyer_id: str
    item_description: str
    target_price_minor: int
    currency: str
    location: str
    status: str

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    post_id: str
    seller_id: str
    caption: Optional[str] = None
    media_url: Optional[str] = None
    price_minor: Optional[int] = None
    currency: Optional[str] = None
    match_score: float
