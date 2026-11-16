from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
import re

class EmailSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_seller: bool = Field(default=False)

    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class EmailLogin(BaseModel):
    email: EmailStr
    password: str

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
