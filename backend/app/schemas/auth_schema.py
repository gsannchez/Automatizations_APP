"""Pydantic schemas for authentication endpoints."""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """Input schema for POST /auth/register."""
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Input schema for POST /auth/login."""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Input schema for POST /auth/refresh."""
    refresh_token: str


class Token(BaseModel):
    """Full token pair returned on login and register."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessToken(BaseModel):
    """New access token returned by the refresh endpoint."""
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    """Public representation of an authenticated user."""
    id: UUID
    email: str
    plan: str
    minutes_used: int
    created_at: datetime

    class Config:
        from_attributes = True
