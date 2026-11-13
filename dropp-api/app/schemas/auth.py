from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class EmailSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    is_seller: bool = Field(default=False, description="True if claiming a link as a seller")

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
