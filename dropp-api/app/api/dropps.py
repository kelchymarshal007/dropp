from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.dropp import DroppCreate, DroppResponse
from app.services import dropp_service
from app.models.dropp import Dropp
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/v1/dropps", tags=["Dropps"])

@router.post("/", response_model=DroppResponse)
async def create_dropp(
    payload: DroppCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # SECURED!
):
    """Creates a new Dropp Card. Requires Authentication."""
    try:
        # We pass str(current_user.id) to ensure it's a string
        dropp = await dropp_service.create_dropp(db, payload, str(current_user.id))
        return dropp
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dropp_code}", response_model=DroppResponse)
async def get_dropp(dropp_code: str, db: AsyncSession = Depends(get_db)):
    """Fetches a Dropp by its short code. Publicly accessible (for sellers clicking links)."""
    result = await db.execute(select(Dropp).where(Dropp.code == dropp_code))
    dropp = result.scalar_one_or_none()
    
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
        
    return dropp
