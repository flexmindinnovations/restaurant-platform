import uuid
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: str | None = None
    roles: list[str] | None = None


class RegisterResponse(BaseModel):
    id: uuid.UUID


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    phone_number: str | None
    is_verified: bool
    is_active: bool
    roles: list[str]
    created_at: datetime
    updated_at: datetime
