import os
import asyncio
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.websockets.chat_manager import chat_manager
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery('dropp_worker', broker=redis_url)

# Thread pool to run blocking Celery calls without stalling the event loop
_executor = ThreadPoolExecutor(max_workers=10)


def _sync_send_task(task_name: str, args: list, queue: str):
    """Blocking Celery send, run inside thread pool."""
    try:
        celery_app.send_task(task_name, args=args, queue=queue)
    except Exception as e:
        print(f"[Notification] Celery send failed for {task_name}: {e}")


async def send_notification(
    db: AsyncSession, 
    user_id: str, 
    notif_type: str, 
    title: str, 
    body: str, 
    channels: Optional[List[str]] = None
):
    if channels is None:
        channels = ["in_app"]

    # 1. Save to DB (In-App inbox)
    notif = Notification(
        user_id=user_id,
        type=notif_type,
        title=title,
        body=body,
        channel="in_app"
    )
    db.add(notif)
    await db.commit()
    await db.refresh(notif)

    # 2. Push to WebSocket (Real-time, non-blocking via Redis)
    try:
        await chat_manager.publish_to_redis(f"user_{user_id}", {
            "type": "notification",
            "title": title,
            "body": body
        })
    except Exception as e:
        print(f"[Notification] WebSocket push failed: {e}")

    # 3. Queue external channel tasks without blocking the event loop
    loop = asyncio.get_running_loop()

    if "email" in channels:
        await loop.run_in_executor(
            _executor,
            _sync_send_task,
            "send_email_notification",
            [user_id, title, body],
            "notifications_email"
        )

    if "sms" in channels:
        await loop.run_in_executor(
            _executor,
            _sync_send_task,
            "send_sms_notification",
            [user_id, title, body],
            "notifications_sms"
        )

    return notif
