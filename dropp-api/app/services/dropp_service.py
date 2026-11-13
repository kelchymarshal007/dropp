import random
import string
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.dropp import Dropp
from app.schemas.dropp import DroppCreate
from app.domain.state_machine import validate_transition
from app.websockets.chat_manager import chat_manager

def generate_short_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def create_dropp(db: AsyncSession, data: DroppCreate, buyer_id: str):
    new_dropp = Dropp(
        code=generate_short_code(),
        buyer_id=buyer_id,
        source_url=data.source_url,
        source_platform=data.source_platform.lower(),
        title=data.title,
        currency=data.currency.upper(),
        offer_minor=data.offer_minor,
        image_url=data.image_url,
        status="sent"
    )
    db.add(new_dropp)
    await db.commit()
    await db.refresh(new_dropp)
    return new_dropp

async def transition_state(db: AsyncSession, dropp: Dropp, new_state: str):
    validate_transition(dropp.status, new_state)
    dropp.status = new_state
    await db.commit()
    await db.refresh(dropp)
    return dropp

async def seller_respond(db: AsyncSession, dropp: Dropp, seller_id: str, availability: str, action: str):
    dropp.seller_id = seller_id
    dropp.availability_type = availability
    
    if action == "decline":
        return await transition_state(db, dropp, "declined")
    
    await chat_manager.inject_agent_action(
        dropp_id=dropp.id,
        body=f"Seller confirmed the item is [{availability}]. The chat is now unlocked. You may negotiate the final price.",
        action_prompt="none" 
    )
    
    return await transition_state(db, dropp, "negotiating")

async def sign_deal(db: AsyncSession, dropp: Dropp, user_id: str, final_minor: int, dispatch_mode: str):
    # 1. SECURITY: Verify user is buyer or seller
    is_buyer = str(user_id) == str(dropp.buyer_id)
    is_seller = str(user_id) == str(dropp.seller_id)
    
    if not is_buyer and not is_seller:
        raise ValueError("You are not a participant in this trade")
    
    # 2. Only allow signing in 'negotiating' state
    if dropp.status != "negotiating":
        raise ValueError(f"Cannot sign in state: {dropp.status}")
    
    # 3. Set terms
    dropp.final_minor = final_minor
    dropp.dispatch_mode = dispatch_mode
    
    # 4. Generate signature hash
    terms = f"{dropp.id}|{final_minor}|{dispatch_mode}|{user_id}"
    sig = hashlib.sha256(terms.encode()).hexdigest()
    
    # 5. Record the signature
    if is_buyer:
        dropp.buyer_signature = sig
        await chat_manager.inject_agent_action(dropp.id, "[AI] Buyer has signed the agreement.", "none")
    if is_seller:
        dropp.seller_signature = sig
        await chat_manager.inject_agent_action(dropp.id, "[AI] Seller has signed the agreement.", "none")
        
    await db.commit()
    await db.refresh(dropp)
    
    # 6. If both have signed, lock the deal
    if dropp.buyer_signature and dropp.seller_signature:
        dropp.checkout_token = generate_short_code(16)
        await db.commit()
        
        await chat_manager.inject_agent_action(
            dropp.id, 
            f"[AI] Agreement locked at {final_minor / 100} {dropp.currency}. Buyer, the secure payment portal is ready.",
            "awaiting_payment"
        )
        await transition_state(db, dropp, "awaiting_payment")
        
    return dropp
