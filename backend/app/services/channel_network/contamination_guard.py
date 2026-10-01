"""
app/services/channel_network/contamination_guard.py

Phase 11.2
Prevents universe bleed, duplicate hooks, and enforces separation rules.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ContaminationGuard:
    def detect_duplicate_hooks(self, new_hook: str, past_hooks: list[str]) -> bool:
        """Basic string similarity heuristic to detect duplicates."""
        new_norm = new_hook.lower().strip()
        for past in past_hooks:
            # simple substring heuristic
            if new_norm in past.lower() or past.lower() in new_norm:
                return True
        return False

    def detect_overlapping_arcs(self, new_arc: str, existing_universes: list[str]) -> bool:
        """Detects if a storyline arc bleeds into another universe."""
        return new_arc in existing_universes

    def calculate_decay_penalty(self, last_used_days_ago: int) -> float:
        """Calculates reuse penalty. Recency decays over time."""
        if last_used_days_ago < 7:
            return 1.0 # High penalty
        elif last_used_days_ago < 30:
            return 0.5
        return 0.0

    def enforce_isolation_threshold(self, overlap_score: float, threshold: float = 0.3) -> bool:
        """Returns True if the content is safe to publish (below threshold)."""
        return overlap_score < threshold
