from sqlmodel import SQLModel, Field
from typing import Optional

class ChannelProfile(SQLModel, table=True):
    """Configuration profile for a channel."""
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channel.id")
    
    # Style preferences
    tone: str = "Professional"  # Professional, Casual, Humorous, Educational
    target_audience: str = "General"
    default_language: str = "Spanish"
    
    # Visual style
    color_palette: Optional[str] = None  # JSON string
    font_family: Optional[str] = None
    
    # Content preferences
    video_duration: int = 60  # seconds
    include_subtitles: bool = True
    include_music: bool = True
    
class ScheduleRule(SQLModel, table=True):
    """Scheduling rules for automatic posting."""
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channel.id")
    
    # Cron-like scheduling
    cron_expression: str  # "0 18 * * *" = daily at 6 PM
    timezone: str = "UTC"
    
    is_active: bool = True
    
class MediaTemplate(SQLModel, table=True):
    """Media assets for channels (intros, outros, etc)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    channel_id: int = Field(foreign_key="channel.id")
    
    template_type: str  # "intro", "outro", "logo"
    file_path: str
    duration: Optional[int] = None  # seconds
