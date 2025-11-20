from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class GeneratedVideo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    channel_id: int = Field(foreign_key="channel.id")
    template_id: int = Field(foreign_key="template.id")

    topic: str
    status: str = "pending"  # pending | success | error
    file_path: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
