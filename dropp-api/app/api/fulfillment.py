from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.dropp import Dropp
from app.models.user import User
from app.schemas.dropp import DroppResponse
from app.api.deps import get_current_user
from app.services import fulfillment_service

router = APIRouter(prefix="/v1/dropps", tags=["Fulfillment"])

@router.post("/{dropp_code}/ship", response_model=DroppResponse)
async def ship_dropp(dropp_code: str, payload: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    if str(current_user.id) != str(dropp.seller_id):
        raise HTTPException(status_code=403, detail="Only the seller can mark as shipped")
    try:
        return await fulfillment_service.mark_shipped(db, dropp, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dropp_code}/delivered", response_model=DroppResponse)
async def delivered(dropp_code: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    try:
        return await fulfillment_service.mark_delivered(db, dropp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dropp_code}/confirm-received", response_model=DroppResponse)
async def confirm_received(dropp_code: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    if str(current_user.id) != str(dropp.buyer_id):
        raise HTTPException(status_code=403, detail="Only the buyer can confirm receipt")
    try:
        return await fulfillment_service.buyer_confirm(db, dropp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dropp_code}/dispute", response_model=DroppResponse)
async def open_dispute(dropp_code: str, payload: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    reason = payload.get("reason", "unspecified")
    try:
        return await fulfillment_service.open_dispute(db, dropp, reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/admin/{dropp_code}/resolve", response_model=DroppResponse)
async def admin_resolve(dropp_code: str, payload: dict, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    decision = payload.get("decision")
    try:
        return await fulfillment_service.admin_resolve(db, dropp, decision)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
