from pydantic import BaseModel, Field, EmailStr, validator
import re


def _validate_password(v: str) -> str:
    if not re.search(r'[A-Z]', v):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', v):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', v):
        raise ValueError('Password must contain at least one number')
    if not re.search(r'[^A-Za-z0-9]', v):
        raise ValueError('Password must contain at least one special character')
    return v


class EmailSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_e164: str = Field(..., min_length=8)
    is_seller: bool = Field(default=False)

    @validator('password')
    def _pw(cls, v):
        return _validate_password(v)


class EmailLogin(BaseModel):
    email: EmailStr
    password: str


class EmailOtpVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)


class PhoneOtpVerify(BaseModel):
    phone_e164: str
    otp_code: str = Field(..., min_length=6, max_length=6)


class PhoneLoginRequest(BaseModel):
    phone_e164: str


class GooglePhoneRequest(BaseModel):
    phone_e164: str


class OTPRequest(BaseModel):
    phone_e164: str


class OTPVerify(BaseModel):
    phone_e164: str
    otp_code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    is_seller: bool
