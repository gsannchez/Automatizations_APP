from pydantic import BaseModel
from typing import List, Optional

class AIScriptRequest(BaseModel):
    topic: str
    template_id: int

class AIScene(BaseModel):
    text: str
    duration: int
    image_prompt: Optional[str] = None

class AIScriptResponse(BaseModel):
    scenes: List[AIScene]
