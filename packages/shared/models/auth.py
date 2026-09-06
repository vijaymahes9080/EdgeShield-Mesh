"""
Authentication and Authorization Schemas
"""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from .enums import UserRole


class User(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPublic(BaseModel):
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class TokenPayload(BaseModel):
    sub: str  # username
    role: UserRole
    exp: int


class LoginRequest(BaseModel):
    username: str
    password: str
