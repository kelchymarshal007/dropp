from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.dropp import Dropp
from app.schemas.admin import PlatformMetrics, DisputeListItem, UserAdminView, SuspendUserRequest
from app.schemas.dropp import DroppResponse
from app.services import admin_service, fulfillment_service
from app.api.deps import get_current_admin

router = APIRouter(prefix="/v1/admin", tags=["Admin"])

@router.get("/metrics", response_model=PlatformMetrics)
async def metrics(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    return await admin_service.get_platform_metrics(db)

@router.get("/disputes", response_model=List[DisputeListItem])
async def list_disputes(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    return await admin_service.list_disputes(db)

@router.post("/dropps/{dropp_code}/resolve", response_model=DroppResponse)
async def resolve_dispute(dropp_code: str, payload: dict, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")

    decision = payload.get("decision")
    if decision not in ["refund_buyer", "release_seller"]:
        raise HTTPException(status_code=400, detail="decision must be 'refund_buyer' or 'release_seller'")

    try:
        return await fulfillment_service.admin_resolve(db, dropp, decision)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users", response_model=List[UserAdminView])
async def list_users(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin), limit: int = Query(50, le=200), offset: int = Query(0, ge=0)):
    result = await db.execute(select(User).order_by(User.created_at.desc()).limit(limit).offset(offset))
    users = result.scalars().all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "phone_e164": u.phone_e164,
            "is_seller": u.is_seller,
            "is_active": u.is_active,
            "role": u.role,
            "tier": u.tier,
            "created_at": u.created_at,
        }
        for u in users
    ]

@router.post("/users/{user_id}/suspend")
async def suspend_user(user_id: str, payload: SuspendUserRequest, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        user = await admin_service.suspend_user(db, user_id, payload.reason)
        return {"status": "suspended", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/users/{user_id}/reactivate")
async def reactivate_user(user_id: str, db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    try:
        user = await admin_service.reactivate_user(db, user_id)
        return {"status": "reactivated", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
