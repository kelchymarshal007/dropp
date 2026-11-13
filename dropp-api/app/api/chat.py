from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.future import select
from app.websockets.chat_manager import chat_manager
from app.core.security import verify_access_token
from app.core.database import AsyncSessionLocal
from app.models.message import Message
from app.models.user import User
from app.models.dropp import Dropp

router = APIRouter()

@router.websocket("/ws/chat/{dropp_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    dropp_id: str, 
    token: str = Query(...)
):
    # 1. Authenticate user
    user_id = verify_access_token(token)
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return

    async with AsyncSessionLocal() as db:
        # 2. Fetch User and Dropp
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        dropp_result = await db.execute(select(Dropp).where(Dropp.id == dropp_id))
        dropp = dropp_result.scalar_one_or_none()

        if not user or not dropp:
            await websocket.close(code=1008, reason="User or Dropp not found")
            return

        # 3. SECURITY CHECK: Are they the Buyer or the Seller?
        is_buyer = str(dropp.buyer_id) == str(user.id)
        is_seller = str(dropp.seller_id) == str(user.id)
        
        if not is_buyer and not is_seller:
            await websocket.close(code=1008, reason="You are not a participant in this trade")
            return

    # 4. Connect
    await chat_manager.connect(websocket, dropp_id)
    
    # 5. Initial AI Greeting based on who joined
    if is_seller and dropp.status == "sent":
        await websocket.send_json({
            "sender_type": "agent",
            "body": "Welcome Seller. Please confirm the availability of this item:",
            "action_prompt": "confirm_availability" # The UI will render buttons for this
        })
    else:
        await websocket.send_json({
            "sender_type": "agent",
            "body": f"Welcome to the trade for {dropp.title}. Negotiating at {dropp.offer_minor / 100} {dropp.currency}."
        })

    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle structured actions from the UI (e.g., button clicks)
            action = data.get("action")
            if action:
                # Broadcast the action to the other party so they see the progress
                await chat_manager.publish_to_redis(dropp_id, {
                    "sender_type": "system",
                    "body": f"User {user_id[:4]} performed action: {action}"
                })
                continue

            # Handle free text messages
            body = data.get("body", "")
            if not body:
                continue

            sender_type = "buyer" if is_buyer else "seller"

            # Save to DB
            async with AsyncSessionLocal() as db:
                new_msg = Message(
                    dropp_id=dropp_id,
                    sender_type=sender_type,
                    sender_id=str(user.id),
                    body=body
                )
                db.add(new_msg)
                await db.commit()
                await db.refresh(new_msg)

                msg_payload = {
                    "id": str(new_msg.id),
                    "dropp_id": dropp_id,
                    "sender_type": sender_type,
                    "sender_id": str(user.id),
                    "body": body,
                    "created_at": new_msg.created_at.isoformat()
                }

            await chat_manager.publish_to_redis(dropp_id, msg_payload)

    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, dropp_id)
