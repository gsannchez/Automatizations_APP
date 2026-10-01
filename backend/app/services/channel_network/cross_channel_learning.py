"""
app/services/channel_network/cross_channel_learning.py
"""
import logging
from typing import List

logger = logging.getLogger(__name__)

class CrossChannelLearning:
    def share_hooks(self, source_hooks: List[str]) -> List[str]:
        """Shares successful hooks between channels."""
        return [f"{hook} (adapted)" for hook in source_hooks]

    def check_duplication(self, hook: str, existing_hooks: List[str]) -> bool:
        """Prevents direct duplication of hooks."""
        return hook in existing_hooks

    def calculate_diversity_score(self, hooks: List[str]) -> float:
        """Maintains diversity score based on unique hooks."""
        unique_hooks = set(hooks)
        return float(len(unique_hooks) / len(hooks) * 100) if hooks else 100.0
