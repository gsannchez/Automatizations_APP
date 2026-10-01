"""
app/services/economy/resource_allocator.py

Phase 11.4
Allocates GPU priority, channel priority, and execution order.
"""
from typing import Dict, Any, List

class ResourceAllocator:
    def calculate_priority(self, value_score: float, growth_rate: float) -> float:
        """Priority logic based on value and growth."""
        return (value_score * 0.6) + (growth_rate * 0.4)

    def allocate_gpu_priority(self, channels: List[Dict[str, float]]) -> Dict[str, float]:
        """Assigns GPU priority fractions based on relative priority scores."""
        priorities = {ch["id"]: self.calculate_priority(ch.get("value_score", 0), ch.get("growth_rate", 0)) for ch in channels}
        total = sum(priorities.values())
        if total == 0:
            return {ch_id: 1.0 / len(channels) for ch_id in priorities}
        return {ch_id: score / total for ch_id, score in priorities.items()}

    def sort_campaign_execution_order(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sorts campaigns by priority for the orchestrator."""
        for c in campaigns:
            c["priority"] = self.calculate_priority(c.get("value_score", 0), c.get("growth_rate", 0))
        return sorted(campaigns, key=lambda x: x["priority"], reverse=True)
