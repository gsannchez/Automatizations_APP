"""Video model with UUID v7 and storage abstraction."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, Text
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.utils.uuid_utils import generate_uuid7


class GeneratedVideo(SQLModel, table=True):
    """Generated video model with production-ready schema.
    
    Attributes:
        id: UUID v7 primary key (time-ordered)
        user_id: Foreign key to User (nullable for Phase 2)
        template_id: Foreign key to Template
        title: Video title
        platform: Target platform (TIKTOK, REELS, SHORTS) - PostgreSQL ENUM
        status: Current status - PostgreSQL ENUM videostatus
        storage_key: Relative storage path (not filesystem path)
        duration_seconds: Video duration in seconds
        error_message: Error details if status is FAILED
        error_step: Step where error occurred - PostgreSQL ENUM
        is_deleted: Soft delete flag
        deleted_at: Deletion timestamp
        retry_count: Retry count for orchestrator crash recovery
        created_at: Creation timestamp
        updated_at: Last update timestamp
        
    Note:
        Progress is derived from status, not stored in database.
    """
    __tablename__ = "video"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    user_id: Optional[UUID] = Field(
        default=None,
        foreign_key="user.id",
        index=True,
        nullable=True
    )
    template_id: UUID = Field(
        foreign_key="template.id",
        nullable=False
    )
    title: str = Field(nullable=False)
    platform: str = Field(nullable=False)  # PostgreSQL ENUM 'platform'
    status: str = Field(default="QUEUED", index=True, nullable=False)  # PostgreSQL ENUM 'videostatus'
    storage_key: Optional[str] = Field(default=None, nullable=True)
    duration_seconds: Optional[float] = Field(default=None, nullable=True)
    error_message: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
    error_step: Optional[str] = Field(default=None, nullable=True)  # PostgreSQL ENUM 'videostatus'
    is_deleted: bool = Field(default=False, nullable=False, index=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    retry_count: int = Field(default=0, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    # Legacy fields for backward compatibility during migration
    channel_id: Optional[int] = Field(default=None, nullable=True)
    topic: Optional[str] = Field(default=None, nullable=True)
