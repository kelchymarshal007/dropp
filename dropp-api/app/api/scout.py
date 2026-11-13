from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.scout import WantedRequest
from app.models.user import User
from app.schemas.scout import WantedRequestCreate, WantedRequestResponse, MatchResponse
from app.services import scout_service
from app.api.deps import get_current_user
from typing import List

router = APIRouter(prefix="/v1/scout", tags=["Dropp Scout"])

@router.post("/requests", response_model=WantedRequestResponse)
async def create_request(
    payload: WantedRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await scout_service.create_wanted_request(db, str(current_user.id), payload)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.get("/requests", response_model=List[WantedRequestResponse])
async def list_my_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(WantedRequest)
        .where(WantedRequest.buyer_id == str(current_user.id))
        .order_by(WantedRequest.created_at.desc())
    )
    return result.scalars().all()

@router.get("/requests/{request_id}/matches", response_model=List[MatchResponse])
async def get_matches(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await scout_service.find_matches(db, request_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/requests/{request_id}/fulfill", response_model=WantedRequestResponse)
async def fulfill(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return await scout_service.fulfill_request(db, request_id, str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
