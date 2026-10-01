"""
app/services/economy/failure_detector.py

Phase 11.4
Heuristically detects low retention, repeated failed hooks, stagnant universes, and dead channels.
"""
from typing import Dict, Any, List

class FailureDetector:
    def evaluate_content(self, retention_score: float, views: int) -> List[str]:
        signals = []
        if retention_score < 20.0:
            signals.append("WASTE_SIGNAL")
        if views < 100:
            signals.append("LOW_VIEWS")
        return signals

    def evaluate_format(self, recent_performance: List[float]) -> str:
        """If format fails multiple times, suggest deprecation."""
        if len(recent_performance) >= 3 and all(score < 30.0 for score in recent_performance[-3:]):
            return "DEPRECATE_FORMAT"
        return "FORMAT_HEALTHY"

    def evaluate_channel(self, monthly_growth: float, days_stagnant: int) -> str:
        """Determines if a channel is completely dead."""
        if days_stagnant > 30 and monthly_growth <= 0:
            return "KILL_CHANNEL_SUGGESTION"
        return "CHANNEL_ACTIVE"
        
    def evaluate_universe(self, arc_completion_rate: float) -> str:
        """Determines if a universe is stagnant."""
        if arc_completion_rate < 10.0:
            return "STAGNANT_UNIVERSE"
        return "UNIVERSE_HEALTHY"
