from pydantic import BaseModel
from typing import Optional

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    structure_json: Optional[str] = None
    recommended_duration: Optional[int] = None
    style: Optional[str] = None

class TemplateRead(TemplateCreate):
    id: int
