"""
app/services/universe_engine/character_evolution.py

Phase 11.3
Ensures characters only evolve through story events or arc transitions.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CharacterEvolutionEngine:
    def evolve_character(self, character: Dict[str, Any], trigger_event: str, arc_transition: bool) -> Dict[str, Any]:
        """Evolves character state strictly via events, logging the metadata."""
        if not arc_transition and not trigger_event:
            raise ValueError("Random personality drift is not allowed. Evolution requires an event or arc transition.")
            
        evolution_log = character.get("evolution_log", [])
        evolution_log.append({
            "trigger": trigger_event,
            "is_arc_transition": arc_transition,
            "status": "evolved"
        })
        
        character["evolution_log"] = evolution_log
        return character
