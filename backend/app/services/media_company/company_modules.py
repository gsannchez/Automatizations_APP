"""
app/services/media_company/company_modules.py

Phase 11: The "CEO Layer" modules for managing the portfolio of channels.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PortfolioManager:
    def rank_channels(self, channels_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks channels by growth and revenue to identify top performers."""
        return sorted(channels_data, key=lambda x: x.get("monetization_score", 0), reverse=True)

class GrowthAllocator:
    def allocate_gpu_quota(self, ranked_channels: List[Dict[str, Any]], total_quota: int) -> Dict[str, int]:
        """Prioritizes GPU rendering time for top performing channels."""
        allocations = {}
        remaining = total_quota
        for i, ch in enumerate(ranked_channels):
            # Top channel gets 50%, next 30%, rest split
            share = int(remaining * 0.5) if i == 0 else int(remaining * 0.3)
            if share == 0: share = 1
            allocations[ch["channel_id"]] = share
            remaining -= share
        return allocations

class RiskManager:
    def kill_failing_strategies(self, channel_data: Dict[str, Any]) -> bool:
        """Determines if a channel format should be abandoned."""
        return channel_data.get("growth_metrics", {}).get("monthly_views", 0) < 500

class ExpansionEngine:
    def recommend_new_niche(self, current_portfolio: List[str]) -> str:
        """Looks for blue ocean niches not currently covered by the portfolio."""
        return "AI History" # Mock recommendation
