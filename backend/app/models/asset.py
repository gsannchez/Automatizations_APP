"""Asset model for tracking generated media."""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.utils.uuid_utils import generate_uuid7


class Asset(SQLModel, table=True):
    """Generated asset (image or audio) tracking.
    
    Attributes:
        id: UUID v7 primary key
        video_id: Foreign key to Video
        type: Asset type - PostgreSQL ENUM assettype (IMAGE, AUDIO)
        storage_key: Relative storage path
        duration_seconds: Asset duration (for audio)
        created_at: Creation timestamp
    """
    __tablename__ = "asset"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    video_id: UUID = Field(
        foreign_key="video.id",
        index=True,
        nullable=False
    )
    type: str = Field(nullable=False)  # PostgreSQL ENUM 'assettype'
    storage_key: str = Field(nullable=False)
    duration_seconds: Optional[float] = Field(default=None, nullable=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
