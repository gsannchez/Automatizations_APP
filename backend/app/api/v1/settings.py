from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from ...core.database import get_async_session
from ...models.user_settings import UserSettings
from ...models.user import User
from ...dependencies.auth import get_current_user
from pydantic import BaseModel

router = APIRouter()

class SettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    preferred_gemini_model: Optional[str] = None
    preferred_image_model: Optional[str] = None

@router.get("/")
async def get_settings(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Retrieve settings for the current user. Create default if not exists."""
    result = await session.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    settings = result.scalars().first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        session.add(settings)
        await session.commit()
        await session.refresh(settings)
    
    return settings

@router.patch("/")
async def update_settings(
    data: SettingsUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Update user settings."""
    result = await session.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    settings = result.scalars().first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        session.add(settings)
    
    if data.gemini_api_key is not None:
        settings.gemini_api_key = data.gemini_api_key
    if data.openai_api_key is not None:
        settings.openai_api_key = data.openai_api_key
    if data.preferred_gemini_model is not None:
        settings.preferred_gemini_model = data.preferred_gemini_model
    if data.preferred_image_model is not None:
        settings.preferred_image_model = data.preferred_image_model
    
    session.add(settings)
    await session.commit()
    await session.refresh(settings)
    return settings
