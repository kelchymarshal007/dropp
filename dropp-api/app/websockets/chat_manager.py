import json
from typing import Dict, List
from fastapi import WebSocket
import redis.asyncio as aioredis
from app.core.config import settings

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.redis: aioredis.Redis = None

    async def connect(self, websocket: WebSocket, dropp_id: str):
        await websocket.accept()
        if dropp_id not in self.active_connections:
            self.active_connections[dropp_id] = []
        self.active_connections[dropp_id].append(websocket)

    def disconnect(self, websocket: WebSocket, dropp_id: str):
        if dropp_id in self.active_connections:
            if websocket in self.active_connections[dropp_id]:
                self.active_connections[dropp_id].remove(websocket)
            if not self.active_connections[dropp_id]:
                del self.active_connections[dropp_id]

    async def broadcast(self, dropp_id: str, message: dict):
        if dropp_id in self.active_connections:
            for connection in self.active_connections[dropp_id]:
                await connection.send_json(message)

    async def publish_to_redis(self, dropp_id: str, message: dict):
        if self.redis:
            await self.redis.publish(f"chat_{dropp_id}", json.dumps(message))
            
    async def inject_agent_action(self, dropp_id: str, body: str, action_prompt: str):
        """Injects a structured AI prompt (e.g., 'Do you accept the price?')"""
        msg = {
            "sender_type": "agent",
            "body": body,
            "action_prompt": action_prompt 
        }
        await self.publish_to_redis(dropp_id, msg)

    async def listen_to_redis(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe("chat_*")
        
        async for message in pubsub.listen():
            if message['type'] == 'pmessage':
                channel = message['channel']
                dropp_id = channel.replace("chat_", "")
                data = json.loads(message['data'])
                await self.broadcast(dropp_id, data)

chat_manager = ChatManager()
