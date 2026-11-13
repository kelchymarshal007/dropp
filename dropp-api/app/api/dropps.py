from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.dropp import DroppCreate, DroppResponse, SellerResponse, SignDeal
from app.services import dropp_service
from app.models.dropp import Dropp
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/v1/dropps", tags=["Dropps"])

@router.post("/", response_model=DroppResponse)
async def create_dropp(payload: DroppCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await dropp_service.create_dropp(db, payload, str(current_user.id))

@router.get("/{dropp_code}", response_model=DroppResponse)
async def get_dropp(dropp_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    return dropp

@router.post("/{dropp_code}/seller-respond", response_model=DroppResponse)
async def seller_respond(dropp_code: str, payload: SellerResponse, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    try:
        return await dropp_service.seller_respond(db, dropp, str(current_user.id), payload.availability_type, payload.action)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{dropp_code}/sign", response_model=DroppResponse)
async def sign_deal(dropp_code: str, payload: SignDeal, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
    try:
        return await dropp_service.sign_deal(db, dropp, str(current_user.id), payload.final_minor, payload.dispatch_mode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
