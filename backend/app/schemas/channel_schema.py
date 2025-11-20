from pydantic import BaseModel
from typing import Optional

class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[str] = None
    export_path: Optional[str] = None

class ChannelRead(ChannelCreate):
    id: int
