"""
app/services/tts/voice_registry.py

Maps characters to voice IDs and styles (ElevenLabs voice IDs when the
ElevenLabs provider is selected).
"""
from typing import Any, Dict


class VoiceRegistry:
    def __init__(self):
        # Default mapping. In production, this would be fetched from DB.
        self.registry: Dict[str, Dict[str, Any]] = {
            "narrator": {
                "voice_id": "pNInz6obbfDQGcgMyIGC",  # Adam
                "emotion_profile": "calm",
            },
            "protagonist": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Rachel
                "emotion_profile": "dramatic",
            },
        }

    def get_voice(self, character_id: str) -> Dict[str, Any]:
        """Returns the voice settings for a character, or fallback to narrator."""
        return self.registry.get(character_id, self.registry["narrator"])
