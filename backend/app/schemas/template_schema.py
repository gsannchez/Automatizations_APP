from pydantic import BaseModel
from typing import Optional, Union, Any, Dict
from uuid import UUID

class TemplateCreate(BaseModel):
    name: str
    platform: str  # TIKTOK, REELS, SHORTS
    description: Optional[str] = None
    structure_json: Optional[str] = None
    # style_config replaces old style? Or coexistence?
    style_config: Optional[Dict[str, Any]] = {}
    
    # Legacy fields mapping logic might occur in API logic or here
    recommended_duration: Optional[int] = None
    style: Optional[str] = None

class TemplateRead(TemplateCreate):
    id: Union[UUID, int]
    is_active: bool = True
