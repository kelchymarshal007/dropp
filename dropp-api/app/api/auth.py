import requests
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
)
from app.models.user import User
from app.schemas.auth import (
    EmailSignup,
    EmailLogin,
    EmailOtpVerify,
    PhoneOtpVerify,
    PhoneLoginRequest,
    GooglePhoneRequest,
    OTPRequest,
    OTPVerify,
    TokenResponse,
)
from app.services import auth_service, otp_service


router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


def set_refresh_cookie(response: Response, user_id: str):
    refresh_token = create_refresh_token({"sub": user_id})
    response.set_cookie(
        key="dropp_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )


def _issue(response: Response, user: User) -> TokenResponse:
    set_refresh_cookie(response, str(user.id))
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "user_id": str(user.id),
        "is_seller": user.is_seller,
    }


# ---------- EMAIL SIGNUP (2-step verify) ----------

@router.post("/signup/email")
async def signup_email(payload: EmailSignup, db: AsyncSession = Depends(get_db)):
    if await auth_service.get_user_by_email(db, payload.email):
        raise HTTPException(400, "Email already registered")
    if await auth_service.get_user_by_phone(db, payload.phone_e164):
        raise HTTPException(400, "Phone already registered")

    await auth_service.create_pending_user(
        db,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone_e164=payload.phone_e164,
        is_seller=payload.is_seller,
    )

    await otp_service.send_email_otp(payload.email)

    return {"status": "ok", "message": "Verification code sent to email"}


@router.post("/signup/verify-email", response_model=TokenResponse)
async def signup_verify_email(
    payload: EmailOtpVerify, 
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    if not otp_service.verify_email_otp(payload.email, payload.otp_code):
        raise HTTPException(400, "Invalid or expired email OTP")
    
    user = await auth_service.mark_email_verified(db, payload.email)
    if not user:
        raise HTTPException(404, "User not found")
    
    await auth_service.touch_last_login(db, user)
    return _issue(response, user)


@router.post("/signup/verify-phone", response_model=TokenResponse)
async def signup_verify_phone(
    payload: PhoneOtpVerify,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    if not otp_service.verify_phone_otp(payload.phone_e164, payload.otp_code):
        raise HTTPException(400, "Invalid or expired phone OTP")
    user = await auth_service.mark_phone_verified(db, payload.phone_e164)
    if not user:
        raise HTTPException(404, "User not found")
    if not user.email_verified:
        raise HTTPException(400, "Email not verified yet")

    await auth_service.touch_last_login(db, user)
    return _issue(response, user)


# ---------- EMAIL LOGIN ----------

@router.post("/login/email", response_model=TokenResponse)
async def login_email(payload: EmailLogin, response: Response, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_email_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(401, "Invalid email or password")
    if not user.email_verified:
        raise HTTPException(403, "Email not verified")
    await auth_service.touch_last_login(db, user)
    return _issue(response, user)


# ---------- PHONE LOGIN (OTP) ----------

@router.post("/login/phone/request")
async def login_phone_request(payload: PhoneLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.get_user_by_phone(db, payload.phone_e164)
    if not user:
        raise HTTPException(404, "Phone number not registered")
    if not user.phone_verified:
        raise HTTPException(403, "Phone not verified")
    await otp_service.send_phone_otp(payload.phone_e164)
    return {"status": "ok", "message": "OTP sent"}


@router.post("/login/phone/verify", response_model=TokenResponse)
async def login_phone_verify(
    payload: PhoneOtpVerify,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    if not otp_service.verify_phone_otp(payload.phone_e164, payload.otp_code):
        raise HTTPException(400, "Invalid or expired OTP")
    user = await auth_service.get_user_by_phone(db, payload.phone_e164)
    if not user:
        raise HTTPException(404, "User not found")
    await auth_service.touch_last_login(db, user)
    return _issue(response, user)


# ---------- REFRESH ----------

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    rt = request.cookies.get("dropp_refresh_token")
    if not rt:
        raise HTTPException(401, "No refresh token")
    try:
        payload = jwt.decode(rt, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid refresh token")

    r = await db.execute(select(User).where(User.id == user_id))
    user = r.scalar_one_or_none()
    if not user:
        raise HTTPException(401, "User not found")
    return _issue(response, user)


# ---------- GOOGLE ----------

class GoogleAuthPayload(BaseModel):
    credential: str


@router.post("/google")
async def google_auth(payload: GoogleAuthPayload, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        r = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.credential}",
            timeout=10,
        )
    except Exception as e:
        raise HTTPException(500, f"Google verification failed: {e}")
    if r.status_code != 200:
        raise HTTPException(400, "Invalid Google token")
    g = r.json()
    email = g.get("email")
    google_id = g.get("sub")
    name = g.get("name") or ""
    picture = g.get("picture")
    given = g.get("given_name", "")
    family = g.get("family_name", "")

    if not email:
        raise HTTPException(400, "Google account has no email")

    rr = await db.execute(select(User).where(User.email == email))
    user = rr.scalar_one_or_none()

    if not user:
        user = User(
            email=email,
            google_id=google_id,
            first_name=given or None,
            last_name=family or None,
            display_name=name or None,
            avatar_url=picture,
            email_verified=True,
            phone_verified=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    await auth_service.touch_last_login(db, user)
    tokens = _issue(response, user)
    return {**tokens, "phone_missing": (user.phone_e164 is None or not user.phone_verified)}


@router.post("/google/phone/request")
async def google_phone_request(payload: GooglePhoneRequest, db: AsyncSession = Depends(get_db)):
    if await auth_service.get_user_by_phone(db, payload.phone_e164):
        raise HTTPException(400, "Phone already registered")
    await otp_service.send_phone_otp(payload.phone_e164)
    return {"status": "ok"}


class GooglePhoneVerify(BaseModel):
    user_id: str
    phone_e164: str
    otp_code: str


@router.post("/google/phone/verify")
async def google_phone_verify(payload: GooglePhoneVerify, db: AsyncSession = Depends(get_db)):
    if not otp_service.verify_phone_otp(payload.phone_e164, payload.otp_code):
        raise HTTPException(400, "Invalid OTP")
    r = await db.execute(select(User).where(User.id == payload.user_id))
    user = r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    if await auth_service.get_user_by_phone(db, payload.phone_e164):
        raise HTTPException(400, "Phone already registered to another account")
    user.phone_e164 = payload.phone_e164
    user.phone_verified = True
    await db.commit()
    return {"status": "ok", "phone_verified": True}


# ---------- LEGACY OTP (kept for compatibility) ----------

@router.post("/otp/request")
async def legacy_otp_request(payload: OTPRequest):
    await otp_service.send_phone_otp(payload.phone_e164)
    return {"status": "ok"}


@router.post("/otp/verify", response_model=TokenResponse)
async def legacy_otp_verify(
    payload: OTPVerify,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    if not otp_service.verify_phone_otp(payload.phone_e164, payload.otp_code):
        raise HTTPException(400, "Invalid or expired OTP")
    user = await auth_service.get_user_by_phone(db, payload.phone_e164)
    if not user:
        raise HTTPException(404, "User not found")
    await auth_service.touch_last_login(db, user)
    return _issue(response, user)
