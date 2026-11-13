from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.auth import EmailSignup, EmailLogin, OTPRequest, OTPVerify, TokenResponse
from app.services import auth_service
from app.core.security import create_access_token

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

@router.post("/signup/email", response_model=TokenResponse)
async def signup_email(payload: EmailSignup, db: AsyncSession = Depends(get_db)):
    user = await auth_service.create_email_user(db, payload.email, payload.password, payload.is_seller)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user_id": str(user.id), "is_seller": user.is_seller}

@router.post("/login/email", response_model=TokenResponse)
async def login_email(payload: EmailLogin, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_email_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user_id": str(user.id), "is_seller": user.is_seller}

@router.post("/otp/request")
async def request_otp(payload: OTPRequest):
    auth_service.generate_otp(payload.phone_e164)
    return {"status": "ok", "message": "OTP sent"}

@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(payload: OTPVerify, db: AsyncSession = Depends(get_db)):
    user = await auth_service.verify_otp_and_get_user(db, payload.phone_e164, payload.otp_code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user_id": str(user.id), "is_seller": user.is_seller}
