from sqlmodel import SQLModel, Field
from typing import Optional

class Channel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    platform: str  # "youtube", "tiktok", "instagram"
    description: Optional[str] = None
    tags: Optional[str] = None
    
    # OAuth credentials (encrypted)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[str] = None
    
    # Platform-specific identifiers
    channel_id: Optional[str] = None  # ID del canal en la plataforma
    
    # Configuration
    is_active: bool = True
    export_path: Optional[str] = None
