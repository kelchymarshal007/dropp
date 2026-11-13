import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models.user import User
from app.models.dropp import Dropp
from app.models.ledger import LedgerEntry
from app.models.post import Post
from app.models.post_social import PostLike, PostComment
from app.models.message import Message
from app.models.scout import WantedRequest
from app.models.notification import Notification
from app.api import dropps, auth, chat, payments, posts, feed, fulfillment, scout, notifications
from app.websockets.chat_manager import chat_manager

app = FastAPI(title="Dropp Core API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(chat_manager.listen_to_redis())
    print("SUCCESS: Database connected and Redis WebSocket listener active.")

app.include_router(auth.router)
app.include_router(dropps.router)
app.include_router(chat.router)
app.include_router(payments.router)
app.include_router(posts.router)
app.include_router(feed.router)
app.include_router(fulfillment.router)
app.include_router(scout.router)
app.include_router(notifications.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "dropp-api"}
