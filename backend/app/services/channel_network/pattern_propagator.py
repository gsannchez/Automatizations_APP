"""
app/services/channel_network/pattern_propagator.py

Phase 11.2
Propagates successful structures across channels and adapts patterns.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PatternPropagator:
    def adapt_pattern(self, base_pattern: str, target_niche: str) -> str:
        """Adapts an abstract pattern to the specific channel niche."""
        if base_pattern == "shock_hook":
            return f"shock_hook_adapted_for_{target_niche}"
        elif base_pattern == "curiosity_loop":
            return f"curiosity_loop_adapted_for_{target_niche}"
        return f"adapted_{base_pattern}"

    def transform_format(self, format_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Transforms format without copying the raw content."""
        transformed = format_spec.copy()
        transformed["is_adapted"] = True
        return transformed
