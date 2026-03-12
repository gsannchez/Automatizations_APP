"""FastAPI dependency: resolve the current authenticated user from a Bearer JWT.

Usage
-----
    from app.dependencies.auth import get_current_user

    @router.get("/me")
    async def me(user: User = Depends(get_current_user)):
        ...
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_async_session
from ..core.security import decode_token
from ..models.user import User

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(_oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Decode the Bearer access token and return the corresponding User.

    Raises:
        HTTPException 401: if the token is missing, invalid, expired, or the
            user no longer exists in the database.
    """
    payload = decode_token(token, expected_type="access")
    user_id: str = payload.get("sub")

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
