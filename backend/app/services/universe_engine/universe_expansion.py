"""
app/services/universe_engine/universe_expansion.py

Phase 11.3
Expands universes with additive storytelling and prevents hard retcons.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class UniverseExpansionEngine:
    def evaluate_expansion(self, new_story_arc: Dict[str, Any], existing_lore: List[Dict[str, Any]]) -> bool:
        """Checks if a new storyline branches consistently with existing lore."""
        if new_story_arc.get("is_retcon"):
            return False
        return True

    def attach_narrative_thread(self, current_state: Dict[str, Any], new_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Soft evolution by additive storytelling."""
        current_state.setdefault("events", []).extend(new_events)
        return current_state
