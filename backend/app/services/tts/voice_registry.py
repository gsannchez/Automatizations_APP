class VoiceRegistry:
    """Simple voice registry shim for tests and local runs."""
    def __init__(self):
        # Minimal registry; extend with real mapping as needed.
        self._voices = {
            "narrator": {"voice_id": "narrator_default"},
            "default": {"voice_id": "narrator_default"}
        }

    def get_voice(self, name: str):
        return self._voices.get(name, self._voices["default"])
"""
app/services/tts/voice_registry.py

Maps characters to ElevenLabs voice IDs and styles.
"""
from typing import Dict, Any

class VoiceRegistry:
    def __init__(self):
        # Default mapping. In production, this would be fetched from DB.
        self.registry = {
            "narrator": {
                "voice_id": "pNInz6obbfDQGcgMyIGC", # Adam
                "emotion_profile": "calm"
            },
            "protagonist": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL", # Rachel
                "emotion_profile": "dramatic"
            }
        }
        
    def get_voice(self, character_id: str) -> Dict[str, Any]:
        """Returns the voice settings for a character, or fallback to narrator."""
        return self.registry.get(character_id, self.registry["narrator"])
