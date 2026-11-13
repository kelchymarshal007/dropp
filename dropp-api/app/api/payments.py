from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.dropp import Dropp
from app.models.user import User
from app.gateways.plugins.mock_gateway import MockGateway
from app.services.dropp_service import transition_state
from app.websockets.chat_manager import chat_manager

router = APIRouter(prefix="/v1/payments", tags=["Payments"])
gateway = MockGateway()

@router.get("/checkout/{checkout_token}")
async def get_checkout_details(checkout_token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dropp).where(Dropp.checkout_token == checkout_token))
    dropp = result.scalar_one_or_none()
    
    if not dropp or dropp.status != "awaiting_payment":
        raise HTTPException(status_code=404, detail="Invalid or expired checkout link")
        
    return {
        "dropp_id": dropp.id,
        "title": dropp.title,
        "final_minor": dropp.final_minor,
        "currency": dropp.currency,
        "dispatch_mode": dropp.dispatch_mode,
        "status": dropp.status
    }

@router.post("/confirm-webhook")
async def confirm_payment(payload: dict, db: AsyncSession = Depends(get_db)):
    """Simulates the BIKEM Webhook. In production, this verifies HMAC."""
    dropp_id = payload.get("dropp_id")
    
    result = await db.execute(select(Dropp).where(Dropp.id == dropp_id))
    dropp = result.scalar_one_or_none()
    
    if not dropp:
        raise HTTPException(status_code=404, detail="Dropp not found")
        
    if dropp.status != "awaiting_payment":
        raise HTTPException(status_code=400, detail=f"Dropp is in {dropp.status} state")
        
    # Transition to funded
    await transition_state(db, dropp, "funded")
    
    # Inject AI Message into Chat
    await chat_manager.inject_agent_action(
        dropp.id,
        f"[AI] Payment confirmed! {dropp.final_minor / 100} {dropp.currency} is now held in escrow. Seller, please dispatch the item.",
        "funded"
    )
    
    return {"status": "ok", "message": "Payment confirmed and escrow funded"}
