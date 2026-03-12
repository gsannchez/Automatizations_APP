"""Authentication API router.

Endpoints
---------
POST /auth/register   – create account, return token pair
POST /auth/login      – verify credentials, return token pair (rate-limited: 5/min)
POST /auth/refresh    – exchange refresh token for new access token
GET  /auth/me         – return current user profile
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_async_session
from ...core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ...core.limiter import limiter
from ...models.user import User
from ...schemas.auth_schema import (
    UserCreate,
    UserLogin,
    RefreshRequest,
    Token,
    AccessToken,
    UserRead,
)
from ...dependencies.auth import get_current_user

router = APIRouter()


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new user account and return a JWT token pair."""
    # Check for duplicate email
    result = await session.execute(select(User).where(User.email == data.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token_data = {"sub": str(user.id)}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


# ---------------------------------------------------------------------------
# Login  (rate-limited: 5 requests / minute / IP)
# ---------------------------------------------------------------------------

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,     # required by slowapi decorator
    data: UserLogin,
    session: AsyncSession = Depends(get_async_session),
):
    """Authenticate a user and return a JWT token pair.

    Rate-limited to 5 requests per minute per IP address.
    """
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token_data = {"sub": str(user.id)}
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------

@router.post("/refresh", response_model=AccessToken)
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Exchange a valid refresh token for a new access token."""
    payload = decode_token(body.refresh_token, expected_type="refresh")
    user_id = payload["sub"]

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return AccessToken(access_token=create_access_token({"sub": user_id}))


# ---------------------------------------------------------------------------
# Me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
