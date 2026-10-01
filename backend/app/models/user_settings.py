from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.utils.uuid_utils import generate_uuid7

class UserSettings(SQLModel, table=True):
    """User-specific configuration for AI models and API keys."""
    __tablename__ = "user_settings"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(foreign_key="user.id", unique=True, nullable=False)
    
    # API Keys
    gemini_api_key: Optional[str] = Field(default=None)
    openai_api_key: Optional[str] = Field(default=None)
    
    # Model Preferences
    preferred_gemini_model: str = Field(default="gemini-1.5-flash")
    preferred_image_model: str = Field(default="dall-e-3")
    
    # Video AI Preferences (Phase 6)
    preferred_video_backend: str = Field(default="auto") # auto, animatediff, svd, kling, runway
    video_quality: str = Field(default="high") # low, medium, high
    max_ai_video_duration: float = Field(default=8.0) # Maximum seconds of AI video per clip to save VRAM
    hybrid_rendering: bool = Field(default=True) # Mix AI video with FFmpeg static motion
    motion_intensity: float = Field(default=0.5) # Global multiplier for motion scheduler
    
    # Advanced Config
    extra_config: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB, nullable=False)
    )
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
