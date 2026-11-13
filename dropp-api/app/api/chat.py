from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.future import select
from app.websockets.chat_manager import chat_manager
from app.core.security import verify_access_token
from app.core.database import AsyncSessionLocal
from app.models.message import Message
from app.models.user import User

router = APIRouter()

@router.websocket("/ws/chat/{dropp_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    dropp_id: str, 
    token: str = Query(...)
):
    # 1. Authenticate the WebSocket connection
    user_id = verify_access_token(token)
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # 2. Fetch user details to know if they are buyer or seller
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            await websocket.close(code=1008, reason="User not found")
            return

    # 3. Connect to the Chat Room
    await chat_manager.connect(websocket, dropp_id)
    
    # 4. Send the initial AI Agent Welcome Message (Only on connect)
    welcome_msg = {
        "sender_type": "agent",
        "sender_id": "dropp_ai",
        "body": "Welcome to Dropp Escrow. Please verify the item availability to begin."
    }
    await websocket.send_json(welcome_msg)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            body = data.get("body", "")
            
            if not body:
                continue

            # Determine sender type (simplified for MVP, normally checked against dropp model)
            sender_type = "buyer" if user.is_seller == False else "seller"

            # Save to Database
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

            # Broadcast to everyone in the room via Redis
            await chat_manager.publish_to_redis(dropp_id, msg_payload)

    except WebSocketDisconnect:
        chat_manager.disconnect(websocket, dropp_id)
