"""Template model with UUID v7 and JSONB config."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from app.utils.uuid_utils import generate_uuid7


class Template(SQLModel, table=True):
    """Video template with style configuration.
    
    Attributes:
        id: UUID v7 primary key
        name: Template name
        platform: Target platform - PostgreSQL ENUM
        style_config: JSONB configuration for image style, checkpoints, etc.
        is_active: Whether template is currently active
        created_at: Creation timestamp
    """
    __tablename__ = "template"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    name: str = Field(nullable=False)
    platform: str = Field(nullable=False)  # PostgreSQL ENUM 'platform'
    style_config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False)
    )
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    # Legacy fields for backward compatibility
    description: Optional[str] = Field(default=None, nullable=True)
    structure_json: Optional[str] = Field(default=None, nullable=True)
