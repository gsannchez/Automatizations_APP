"""
app/services/universe_engine/story_arc_engine.py

Phase 11.3
Manages structured arcs (INTRO, DEVELOPMENT, CLIMAX, RESOLUTION).
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class StoryArcEngine:
    VALID_STAGES = ["INTRO", "DEVELOPMENT", "CLIMAX", "RESOLUTION"]

    def __init__(self):
        self.arcs = {}

    def start_arc(self, universe_id: str, arc_name: str, is_dominant: bool = True) -> Dict[str, Any]:
        """Starts a new arc if no dominant arc is unfinished."""
        if is_dominant and self._has_unfinished_dominant_arc(universe_id):
            raise ValueError(f"Universe {universe_id} already has an unfinished dominant arc.")
            
        arc = {
            "name": arc_name,
            "stage": "INTRO",
            "is_dominant": is_dominant,
            "status": "active"
        }
        self.arcs.setdefault(universe_id, []).append(arc)
        return arc

    def progress_arc(self, arc: Dict[str, Any]) -> Dict[str, Any]:
        """Progresses the arc to the next stage."""
        current_idx = self.VALID_STAGES.index(arc["stage"])
        if current_idx < len(self.VALID_STAGES) - 1:
            arc["stage"] = self.VALID_STAGES[current_idx + 1]
        if arc["stage"] == "RESOLUTION":
            arc["status"] = "completed"
        return arc

    def _has_unfinished_dominant_arc(self, universe_id: str) -> bool:
        """Checks for unfinished dominant arcs."""
        for arc in self.arcs.get(universe_id, []):
            if arc["is_dominant"] and arc["status"] != "completed":
                return True
        return False
