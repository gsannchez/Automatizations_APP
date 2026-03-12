"""Generated video schemas with UUID v7 and computed progress."""
from pydantic import BaseModel, computed_field
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.utils.progress_utils import get_progress_from_status


class GeneratedVideoCreate(BaseModel):
    """Schema for creating a new video."""
    template_id: UUID
    title: str
    platform: str  # TIKTOK, REELS, SHORTS
    topic: Optional[str] = None  # Legacy field
    channel_id: Optional[int] = None  # Legacy field


class GeneratedVideoRead(BaseModel):
    """Schema for reading video data with computed progress.
    
    Progress is derived from status, not stored in database.
    """
    id: UUID
    user_id: Optional[UUID]
    template_id: UUID
    title: str
    platform: str
    status: str
    storage_key: Optional[str]
    duration_seconds: Optional[float]
    error_message: Optional[str]
    error_step: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Legacy fields
    topic: Optional[str] = None
    channel_id: Optional[int] = None
    
    @computed_field
    @property
    def progress(self) -> int:
        """Compute progress percentage from status.
        
        Returns:
            int: Progress percentage (0-100)
        """
        return get_progress_from_status(self.status)

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class GeneratedVideoStatus(BaseModel):
    """Lightweight schema for status polling."""
    id: UUID
    status: str

    @computed_field
    @property
    def progress(self) -> int:
        """Compute progress percentage from status."""
        return get_progress_from_status(self.status)

    class Config:
        from_attributes = True


class GeneratedVideoPage(BaseModel):
    """Paginated response for GET /videos."""
    items: list[GeneratedVideoRead]
    total: int
    page: int
    limit: int
