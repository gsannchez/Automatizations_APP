from pydantic import BaseModel, field_validator, model_validator
from typing import Any, List, Optional, Union
from uuid import UUID

class AIScriptRequest(BaseModel):
    topic: str
    template_id: Union[UUID, int]  # Allow both for backward compatibility or migration transition
    tone: Optional[str] = "Professional"
    target_audience: Optional[str] = "General"
    language: Optional[str] = "Spanish"
    platform: Optional[str] = "YouTube"
    # Per-user LLM overrides (loaded from UserSettings in tasks/scripting.py)
    api_key: Optional[str] = None
    model_name: Optional[str] = None

class AIScene(BaseModel):
    text: str = ""
    duration: int = 5
    image_prompt: Optional[str] = None
    # Additional art-direction fields (all optional so older templates/tests
    # keep working). They flow straight into ``scenes_data``.
    voiceover_text: Optional[str] = None
    visual_style: Optional[str] = None
    camera_move: Optional[str] = None
    character: Optional[str] = None
    emotion: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    sfx: Optional[str] = None
    on_screen_text: Optional[str] = None
    language: Optional[str] = None

    @field_validator("duration", mode="before")
    @classmethod
    def _coerce_duration(cls, value: Any) -> int:
        """LLMs often emit floats or numeric strings for the duration."""
        if value is None:
            return 5
        try:
            return max(1, int(round(float(value))))
        except (TypeError, ValueError):
            return 5

    @field_validator("seed", mode="before")
    @classmethod
    def _coerce_seed(cls, value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @model_validator(mode="after")
    def _ensure_text(self) -> "AIScene":
        """Some responses only carry ``voiceover_text``/``on_screen_text``."""
        if not self.text:
            self.text = self.voiceover_text or self.on_screen_text or ""
        return self

class AIScriptResponse(BaseModel):
    scenes: List[AIScene]


class AITextEnhanceRequest(BaseModel):
    """Body of POST /ai/enhance-text (matches the Angular ``ai.service.ts``)."""
    title: str
    topic: str


class AITextEnhanceResponse(BaseModel):
    title: str
    topic: str
