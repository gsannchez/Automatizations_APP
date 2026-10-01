"""
app/services/media_company/company_orchestrator.py

Phase 11: Master orchestrator that acts as an autonomous CEO, managing 
channels, allocating GPU limits, and launching new niches.
"""
import logging
from typing import Dict, Any, List

from .company_modules import PortfolioManager, GrowthAllocator, RiskManager, ExpansionEngine

logger = logging.getLogger(__name__)

class CompanyOrchestrator:
    def __init__(self):
        self.portfolio = PortfolioManager()
        self.allocator = GrowthAllocator()
        self.risk = RiskManager()
        self.expansion = ExpansionEngine()

    def run_weekly_board_meeting(self, tenant_id: str, channels_data: List[Dict[str, Any]], total_gpu_quota: int) -> Dict[str, Any]:
        """
        Executes top-level strategic decisions: scaling winners, killing losers, allocating GPUs.
        """
        logger.info(f"[CompanyOrchestrator] Running strategy board for tenant {tenant_id}")
        
        # 1. Rank Portfolio
        ranked = self.portfolio.rank_channels(channels_data)
        
        # 2. Kill / Pivot losers
        actions = []
        active_channels = []
        for ch in ranked:
            if self.risk.kill_failing_strategies(ch):
                actions.append(f"Pivot channel {ch['channel_id']} due to stagnation.")
            else:
                active_channels.append(ch)
                
        # 3. Allocate GPUs to survivors
        quotas = self.allocator.allocate_gpu_quota(active_channels, total_gpu_quota)
        
        # 4. Expansion
        if len(active_channels) < 3: # Mock threshold
            new_niche = self.expansion.recommend_new_niche([c.get("niche") for c in active_channels])
            actions.append(f"Launch new channel in niche: {new_niche}")
            
        return {
            "tenant_id": tenant_id,
            "gpu_allocations": quotas,
            "strategic_actions": actions,
            "top_channel": active_channels[0]["channel_id"] if active_channels else None
        }
