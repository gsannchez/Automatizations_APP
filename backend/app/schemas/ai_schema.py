from pydantic import BaseModel
from typing import List, Optional, Union
from uuid import UUID

class AIScriptRequest(BaseModel):
    topic: str
    template_id: Union[UUID, int]  # Allow both for backward compatibility or migration transition
    tone: Optional[str] = "Professional"
    target_audience: Optional[str] = "General"
    language: Optional[str] = "Spanish"
    platform: Optional[str] = "YouTube"

class AIScene(BaseModel):
    text: str
    duration: int
    image_prompt: Optional[str] = None

class AIScriptResponse(BaseModel):
    scenes: List[AIScene]
