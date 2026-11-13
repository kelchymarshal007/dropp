#!/bin/bash

echo "Building Stage 3: Dropp Core API..."

# 1. Pydantic Schemas for Data Validation
cat > dropp-api/app/schemas/dropp.py << 'PY'
from pydantic import BaseModel, Field
from typing import Optional

class DroppCreate(BaseModel):
    buyer_id: str = Field(..., description="The ID of the buyer creating the Dropp")
    source_url: str = Field(..., description="The Instagram/TikTok link")
    source_platform: str = Field(..., description="instagram, tiktok, whatsapp")
    title: str = Field(..., description="Name of the item")
    currency: str = Field(..., description="Currency code (NGN, KES, USD) - NO HARDCODING")
    offer_minor: int = Field(..., description="Offer amount in minor units (kobo/cents)")
    image_url: Optional[str] = None

class DroppResponse(BaseModel):
    id: str
    code: str
    buyer_id: str
    seller_id: Optional[str] = None
    title: str
    status: str
    currency: str
    offer_minor: int
    
    class Config:
        from_attributes = True
PY

# 2. Service Layer (Business Logic)
cat > dropp-api/app/services/dropp_service.py << 'PY'
import random
import string
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dropp import Dropp
from app.schemas.dropp import DroppCreate

def generate_short_code(length=8):
    """Generates a random URL-safe short code (e.g., x7Kp2aB9)"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def create_dropp(db: AsyncSession, data: DroppCreate):
    # Ensure currency is uppercase (e.g., NGN, not ngn)
    currency_upper = data.currency.upper()
    
    new_dropp = Dropp(
        code=generate_short_code(),
        buyer_id=data.buyer_id,
        source_url=data.source_url,
        source_platform=data.source_platform.lower(),
        title=data.title,
        currency=currency_upper,
        offer_minor=data.offer_minor,
        image_url=data.image_url,
        status="sent" # Default state according to the State Machine
    )
    
    db.add(new_dropp)
    await db.commit()
    await db.refresh(new_dropp)
    return new_dropp
PY

# 3. API Routes
cat > dropp-api/app/api/dropps.py << 'PY'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.dropp import DroppCreate, DroppResponse
from app.services import dropp_service
from app.models.dropp import Dropp

router = APIRouter(prefix="/v1/dropps", tags=["Dropps"])

@router.post("/", response_model=DroppResponse)
async def create_dropp(payload: DroppCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new Dropp Card."""
    try:
        dropp = await dropp_service.create_dropp(db, payload)
        return dropp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dropp_code}", response_model=DroppResponse)
async def get_dropp(dropp_code: str, db: AsyncSession = Depends(get_db)):
    """Fetches a Dropp by its short code (e.g., x7Kp2aB9)."""
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
        
    return dropp
PY

# 4. Update main.py to include the router
cat > dropp-api/app/main.py << 'PY'
from fastapi import FastAPI
from app.core.database import engine, Base
from app.models.user import User
from app.models.dropp import Dropp
from app.models.ledger import LedgerEntry
from app.models.post import Post
from app.domain.state_machine import validate_transition
from app.api import dropps

app = FastAPI(title="Dropp Core API", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("SUCCESS: Database connected and all tables created.")

app.include_router(dropps.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "dropp-api"}

@app.post("/test-state-machine")
def test_state_machine(current: str, target: str):
    try:
        validate_transition(current, target)
        return {"status": "ok", "message": f"Valid transition: {current} -> {target}"}
    except ValueError as e:
        return {"status": "error", "message": str(e)}
PY

echo "Stage 3 files created successfully."
