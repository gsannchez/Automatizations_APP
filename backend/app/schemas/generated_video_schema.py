from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GeneratedVideoCreate(BaseModel):
    channel_id: int
    template_id: int
    topic: str

class GeneratedVideoRead(BaseModel):
    id: int
    channel_id: int
    template_id: int
    topic: str
    status: str
    file_path: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
