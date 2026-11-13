from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dropp import Dropp
from app.domain.state_machine import validate_transition
from app.websockets.chat_manager import chat_manager

async def _safe_inject(dropp_id: str, body: str, action_prompt: str):
    try:
        await chat_manager.inject_agent_action(dropp_id, body, action_prompt)
    except Exception as e:
        print(f"[Fulfillment] Warning: Chat injection failed: {e}")

async def mark_shipped(db: AsyncSession, dropp: Dropp, tracking_info: dict):
    validate_transition(dropp.status, "shipped")
    dropp.status = "shipped"
    dropp.shipped_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(dropp)
    
    await _safe_inject(
        dropp.id,
        f"[AI] Seller marked as SHIPPED. Tracking: {tracking_info.get('carrier', 'N/A')} - {tracking_info.get('tracking_no', 'N/A')}. Buyer, please confirm when you receive it.",
        "none"
    )
    return dropp

async def mark_delivered(db: AsyncSession, dropp: Dropp):
    validate_transition(dropp.status, "delivered")
    dropp.status = "delivered"
    dropp.delivered_at = datetime.now(timezone.utc)
    dropp.auto_release_at = datetime.now(timezone.utc) + timedelta(hours=24)
    await db.commit()
    await db.refresh(dropp)
    
    await _safe_inject(
        dropp.id,
        "[AI] Item DELIVERED. Buyer, you have 24 hours to confirm receipt or open a dispute. After that, funds will auto-release to the seller.",
        "confirm_received_or_dispute"
    )
    return dropp

async def buyer_confirm(db: AsyncSession, dropp: Dropp):
    validate_transition(dropp.status, "completed")
    dropp.status = "completed"
    await db.commit()
    await db.refresh(dropp)
    
    await _safe_inject(
        dropp.id,
        "[AI] Buyer confirmed receipt. Trade COMPLETE. Funds released to seller.",
        "completed"
    )
    return dropp

async def open_dispute(db: AsyncSession, dropp: Dropp, reason: str):
    validate_transition(dropp.status, "disputed")
    dropp.status = "disputed"
    await db.commit()
    await db.refresh(dropp)
    
    await _safe_inject(
        dropp.id,
        f"[AI] DISPUTE OPENED. Reason: {reason}. Funds are FROZEN. Both parties must submit evidence within 72 hours. An admin will resolve.",
        "dispute_opened"
    )
    return dropp

async def admin_resolve(db: AsyncSession, dropp: Dropp, decision: str):
    if decision == "refund_buyer":
        validate_transition(dropp.status, "refunded")
        dropp.status = "refunded"
    elif decision == "release_seller":
        validate_transition(dropp.status, "completed")
        dropp.status = "completed"
    else:
        raise ValueError("Invalid decision. Use 'refund_buyer' or 'release_seller'")
        
    await db.commit()
    await db.refresh(dropp)
    
    await _safe_inject(
        dropp.id,
        f"[AI] Dispute RESOLVED by Admin. Decision: {decision}. Trade closed.",
        "completed"
    )
    return dropp
