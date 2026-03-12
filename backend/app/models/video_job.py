"""VideoJob model for step-level tracking."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.utils.uuid_utils import generate_uuid7


class VideoJob(SQLModel, table=True):
    """Video job tracking for idempotent workflow.
    
    Tracks each step of video generation to enable crash recovery
    and resume from last successful step.
    
    Attributes:
        id: UUID v7 primary key
        video_id: Foreign key to Video
        step: Workflow step - PostgreSQL ENUM videostatus
        started_at: When step started
        ended_at: When step completed (nullable if still running)
        success: Whether step completed successfully
        error_message: Error details if failed
    """
    __tablename__ = "videojob"
    
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
    step: str = Field(nullable=False)  # PostgreSQL ENUM 'videostatus'
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    ended_at: Optional[datetime] = Field(default=None, nullable=True)
    success: bool = Field(default=False, nullable=False)
    error_message: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True)
    )
