from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from app.models.user import User
from app.core.security import get_password_hash, verify_password


async def get_user_by_email(db: AsyncSession, email: str):
    r = await db.execute(select(User).where(User.email == email))
    return r.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str):
    r = await db.execute(select(User).where(User.phone_e164 == phone))
    return r.scalar_one_or_none()


async def create_pending_user(
    db: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    phone_e164: str,
    is_seller: bool,
) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        display_name=f"{first_name} {last_name}".strip(),
        phone_e164=phone_e164,
        is_seller=is_seller,
        email_verified=False,
        phone_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def mark_email_verified(db: AsyncSession, email: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    user.email_verified = True
    await db.commit()
    await db.refresh(user)
    return user


async def mark_phone_verified(db: AsyncSession, phone: str):
    user = await get_user_by_phone(db, phone)
    if not user:
        return None
    user.phone_verified = True
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_email_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def touch_last_login(db: AsyncSession, user: User) -> None:
    user.last_login = datetime.utcnow()
    await db.commit()
