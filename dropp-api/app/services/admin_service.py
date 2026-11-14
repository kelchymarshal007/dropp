from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, update
from app.models.user import User
from app.models.dropp import Dropp

async def get_platform_metrics(db: AsyncSession) -> dict:
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_sellers = (await db.execute(select(func.count(User.id)).where(User.is_seller == True))).scalar() or 0
    total_dropps = (await db.execute(select(func.count(Dropp.id)))).scalar() or 0
    
    funded_dropps = (await db.execute(
        select(func.count(Dropp.id)).where(Dropp.status.in_(["funded", "shipped", "delivered"]))
    )).scalar() or 0
    
    disputed_dropps = (await db.execute(
        select(func.count(Dropp.id)).where(Dropp.status == "disputed")
    )).scalar() or 0
    
    completed_dropps = (await db.execute(
        select(func.count(Dropp.id)).where(Dropp.status == "completed")
    )).scalar() or 0

    gmv = (await db.execute(
        select(func.coalesce(func.sum(Dropp.final_minor), 0)).where(
            Dropp.status.in_(["funded", "shipped", "delivered", "completed"])
        )
    )).scalar() or 0

    escrow = (await db.execute(
        select(func.coalesce(func.sum(Dropp.final_minor), 0)).where(
            Dropp.status.in_(["funded", "shipped", "delivered"])
        )
    )).scalar() or 0

    return {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "total_dropps": total_dropps,
        "funded_dropps": funded_dropps,
        "disputed_dropps": disputed_dropps,
        "completed_dropps": completed_dropps,
        "total_gmv_minor": int(gmv),
        "total_escrow_held_minor": int(escrow),
    }

async def list_disputes(db: AsyncSession) -> list:
    result = await db.execute(
        select(Dropp).where(Dropp.status == "disputed").order_by(Dropp.updated_at.asc())
    )
    dropps = result.scalars().all()
    now = datetime.now(timezone.utc)
    items = []
    
    for d in dropps:
        disputed_at = d.updated_at or now
        if disputed_at.tzinfo is None:
            disputed_at = disputed_at.replace(tzinfo=timezone.utc)
        hours = (now - disputed_at).total_seconds() / 3600
        
        items.append({
            "dropp_id": str(d.id),
            "dropp_code": d.code,
            "title": d.title,
            "currency": d.currency,
            "final_minor": d.final_minor,
            "status": d.status,
            "buyer_id": str(d.buyer_id),
            "seller_id": str(d.seller_id) if d.seller_id else None,
            "disputed_at": disputed_at,
            "hours_since_dispute": round(hours, 1),
        })
    return items

async def suspend_user(db: AsyncSession, user_id: str, reason: str):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    if user.role == "admin":
        raise ValueError("Cannot suspend an admin")

    await db.execute(update(User).where(User.id == user_id).values(is_active=False))
    await db.commit()
    return user

async def reactivate_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    await db.execute(update(User).where(User.id == user_id).values(is_active=True))
    await db.commit()
    return user
