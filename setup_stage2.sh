#!/bin/bash

echo "Building Stage 2: Data Layer & State Machine..."

# 1. Base Model (UUIDs and Timestamps for all tables)
cat > dropp-api/app/models/base.py << 'PY'
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
PY

# 2. User Model
cat > dropp-api/app/models/user.py << 'PY'
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
PY

# 3. Dropp Model (The Core Escrow Table)
cat > dropp-api/app/models/dropp.py << 'PY'
from sqlalchemy import Column, String, BigInteger, Integer
from app.models.base import BaseModel

class Dropp(BaseModel):
    __tablename__ = "dropps"
    
    code = Column(String(10), unique=True, index=True, nullable=False)
    buyer_id = Column(String, index=True, nullable=False)
    seller_id = Column(String, index=True, nullable=True)
    
    source_url = Column(String, nullable=False)
    source_platform = Column(String, nullable=False) # instagram, tiktok, whatsapp
    
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    # NO HARDCODED CURRENCIES. Comes from payload.
    currency = Column(String(3), nullable=False) 
    
    # Money in minor units (kobo, cents)
    offer_minor = Column(BigInteger, nullable=False)
    final_minor = Column(BigInteger, nullable=True)
    fee_minor = Column(BigInteger, nullable=True)
    
    status = Column(String, default="draft", nullable=False, index=True)
    version = Column(Integer, default=0, nullable=False) # For optimistic locking
PY

# 4. Append-Only Ledger Model
cat > dropp-api/app/models/ledger.py << 'PY'
from sqlalchemy import Column, String, BigInteger, ForeignKey
from app.models.base import BaseModel

class LedgerEntry(BaseModel):
    __tablename__ = "ledger_entries"
    
    dropp_id = Column(String, nullable=False, index=True)
    entry_type = Column(String, nullable=False) # ESCROW_HELD, ESCROW_RELEASED, FEE_EARNED, REFUND
    amount_minor = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False)
    meta_data = Column(String, nullable=True) # JSON string for extra info
PY

# 5. Posts Model (Dropp Reels Update)
cat > dropp-api/app/models/post.py << 'PY'
from sqlalchemy import Column, String, BigInteger
from app.models.base import BaseModel

class Post(BaseModel):
    __tablename__ = "posts"
    
    seller_id = Column(String, index=True, nullable=False)
    media_url = Column(String, nullable=False)
    media_type = Column(String(10), nullable=False) # video or image
    caption = Column(String, nullable=True)
    
    # Price is optional (for quick drops)
    price_minor = Column(BigInteger, nullable=True)
    currency = Column(String(3), nullable=False) 
    
    status = Column(String, default="active", nullable=False)
PY

# 6. The Deterministic State Machine
cat > dropp-api/app/domain/state_machine.py << 'PY'
from typing import Dict, Set

# Strictly enforced transitions based on DROPP_PROJECT_SCOPE.md
STATES = {
    "draft": {"sent", "cancelled"},
    "sent": {"viewed", "declined", "expired", "cancelled"},
    "viewed": {"negotiating", "declined", "expired", "cancelled"},
    "negotiating": {"agreed", "declined", "expired", "cancelled"},
    "agreed": {"awaiting_payment", "expired"},
    "awaiting_payment": {"funded", "expired"},
    "funded": {"shipped", "disputed", "refunded"},
    "shipped": {"delivered", "disputed"},
    "delivered": {"completed", "disputed"},
    "disputed": {"refunded", "completed"},
    # Terminal states
    "completed": set(),
    "refunded": set(),
    "declined": set(),
    "expired": set(),
    "cancelled": set()
}

def validate_transition(current_state: str, new_state: str) -> bool:
    if current_state not in STATES:
        raise ValueError(f"Unknown current state: {current_state}")
    
    allowed = STATES[current_state]
    if new_state not in allowed:
        raise ValueError(f"Invalid transition from '{current_state}' to '{new_state}'. Allowed: {allowed}")
        
    return True
PY

# 7. Update main.py to load all models on startup
cat > dropp-api/app/main.py << 'PY'
from fastapi import FastAPI
from app.core.database import engine, Base
# Import all models so SQLAlchemy creates the tables
from app.models.user import User
from app.models.dropp import Dropp
from app.models.ledger import LedgerEntry
from app.models.post import Post
from app.domain.state_machine import validate_transition

app = FastAPI(title="Dropp Core API", version="1.0.0")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    print("SUCCESS: Database connected and all tables created.")

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

echo "Stage 2 files created successfully."
