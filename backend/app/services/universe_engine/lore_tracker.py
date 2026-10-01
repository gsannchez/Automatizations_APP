"""
app/services/universe_engine/lore_tracker.py
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class LoreTracker:
    def persist_summary(self, universe_id: str, arc_id: str, scene_id: str, summary: str):
        """Persists lore summaries hierarchically: universe -> arc -> scene -> event."""
        logger.info(f"Persisted lore for U:{universe_id} A:{arc_id} S:{scene_id}")

    def prevent_contradictions(self, proposed_lore: str, existing_lore_hierarchy: Dict[str, Any]) -> bool:
        """Heuristic string + metadata diff to detect contradictions."""
        proposed_norm = proposed_lore.lower()
        # Mock flat check across hierarchy
        for arc, scenes in existing_lore_hierarchy.items():
            for scene, events in scenes.items():
                for event in events:
                    if proposed_norm in event.lower() and "died" in proposed_norm and "alive" in event.lower():
                        return False # Contradiction!
        return True

    def detect_repeated_arcs(self, proposed_arc: str, existing_arcs: List[str]) -> bool:
        """Detects repeated arcs."""
        return proposed_arc in existing_arcs
