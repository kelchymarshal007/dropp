import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.core.security import get_password_hash, verify_password

otp_store = {} # In-memory OTP storage (Move to Redis in production)

async def create_email_user(db: AsyncSession, email: str, password: str, is_seller: bool):
    # Check if exists
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        return None
    
    new_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_seller=is_seller
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_email_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def generate_otp(phone: str) -> str:
    otp = str(random.randint(100000, 999999))
    otp_store[phone] = otp
    print(f"--- MOCK SMS TO {phone} ---")
    print(f"YOUR DROPP OTP IS: {otp}")
    return otp

async def verify_otp_and_get_user(db: AsyncSession, phone: str, code: str):
    if otp_store.get(phone) != code:
        return None
    del otp_store[phone]
    
    result = await db.execute(select(User).where(User.phone_e164 == phone))
    user = result.scalar_one_or_none()
    if not user:
        user = User(phone_e164=phone)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
