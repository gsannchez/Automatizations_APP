"""
app/services/universe_engine/character_memory.py
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CharacterMemory:
    def __init__(self):
        # mock memory persistence
        self.memory_store = {}

    def track_recurring(self, character_data: Dict[str, Any]):
        """Tracks recurring characters and caches their baseline profile."""
        char_id = character_data.get("id")
        if char_id not in self.memory_store:
            self.memory_store[char_id] = character_data

    def maintain_emotional_continuity(self, character_id: str, new_emotion: str) -> bool:
        """Enforces personality stability by checking if new emotion contradicts base."""
        base_profile = self.memory_store.get(character_id, {})
        base_emotion = base_profile.get("emotional_profile", {}).get("baseline", "neutral")
        
        # Heuristic contradiction check
        contradictions = {
            "stoic": ["hysterical", "overly_joyful"],
            "cowardly": ["brave_without_reason", "fearless"]
        }
        
        if new_emotion in contradictions.get(base_emotion, []):
            logger.warning(f"Personality drift detected for {character_id}: {base_emotion} -> {new_emotion}")
            return False
            
        return True

    def expose_helpers(self, character_id: str) -> str:
        """Exposes prompt context helpers."""
        profile = self.memory_store.get(character_id, {})
        return f"[Character: {profile.get('name', 'Unknown')} | Emotion: {profile.get('emotional_profile', {}).get('baseline', 'neutral')}]"
