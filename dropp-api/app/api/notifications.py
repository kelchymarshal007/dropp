from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/v1/notifications", tags=["Notifications"])


@router.get("/")
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == str(current_user.id))
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifications = result.scalars().all()
    return [{
        "id": str(n.id),
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat()
    } for n in notifications]


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await db.execute(
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.user_id == str(current_user.id)
        )
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "ok"}
