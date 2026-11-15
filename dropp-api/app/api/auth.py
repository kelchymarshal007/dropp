from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.schemas.auth import EmailSignup, EmailLogin, OTPRequest, OTPVerify, TokenResponse
from app.services import auth_service
from app.core.security import create_access_token, create_refresh_token, verify_access_token
from app.models.user import User
from jose import jwt, JWTError
from app.core.security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/v1/auth", tags=["Authentication"])

def set_refresh_cookie(response: Response, user_id: str):
    refresh_token = create_refresh_token({"sub": user_id})
    response.set_cookie(
        key="dropp_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True, # Set to True in production (HTTPS)
        samesite="lax",
        max_age=30 * 24 * 60 * 60
    )

@router.post("/signup/email", response_model=TokenResponse)
async def signup_email(payload: EmailSignup, response: Response, db: AsyncSession = Depends(get_db)):
    user = await auth_service.create_email_user(db, payload.email, payload.password, payload.is_seller)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    set_refresh_cookie(response, str(user.id))
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user_id": str(user.id), "is_seller": user.is_seller}

@router.post("/login/email", response_model=TokenResponse)
async def login_email(payload: EmailLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_email_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    set_refresh_cookie(response, str(user.id))
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user_id": str(user.id), "is_seller": user.is_seller}

@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(payload: OTPVerify, response: Response, db: AsyncSession = Depends(get_db)):
    user = await auth_service.verify_otp_and_get_user(db, payload.phone_e164, payload.otp_code)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    set_refresh_cookie(response, str(user.id))
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user_id": str(user.id), "is_seller": user.is_seller}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("dropp_refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    new_access = create_access_token({"sub": str(user.id)})
    return {"access_token": new_access, "user_id": str(user.id), "is_seller": user.is_seller}
