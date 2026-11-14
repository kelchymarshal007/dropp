from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class DisputeListItem(BaseModel):
    dropp_id: str
    dropp_code: str
    title: str
    currency: str
    final_minor: Optional[int]
    status: str
    buyer_id: str
    seller_id: Optional[str]
    disputed_at: datetime
    hours_since_dispute: float

class PlatformMetrics(BaseModel):
    total_users: int
    total_sellers: int
    total_dropps: int
    funded_dropps: int
    disputed_dropps: int
    completed_dropps: int
    total_gmv_minor: int
    total_escrow_held_minor: int

class UserAdminView(BaseModel):
    id: str
    email: Optional[str] = None
    phone_e164: Optional[str] = None
    is_seller: bool
    is_active: bool
    role: str
    tier: str
    created_at: Optional[datetime] = None

class SuspendUserRequest(BaseModel):
    reason: str
