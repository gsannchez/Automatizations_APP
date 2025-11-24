from pydantic import BaseModel
from typing import List, Optional

class AIScriptRequest(BaseModel):
    topic: str
    template_id: int
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
