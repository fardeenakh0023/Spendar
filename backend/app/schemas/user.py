import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", v):
            raise ValueError("must be 3-30 characters: letters, numbers, dot, dash or underscore")
        return v

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("must be at least 8 characters")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("must be at most 72 bytes")
        return v


class LoginRequest(BaseModel):
    identifier: str  # username or email
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


class AuthOut(BaseModel):
    user: UserOut
    csrf_token: str
