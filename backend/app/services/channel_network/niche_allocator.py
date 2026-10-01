"""
app/services/channel_network/niche_allocator.py
"""
import logging
from typing import List

logger = logging.getLogger(__name__)

class NicheAllocator:
    def allocate_niche(self, desired_niche: str, existing_niches: List[str]) -> str:
        """Heuristic niche diversification and overlap prevention."""
        if desired_niche.lower() in [n.lower() for n in existing_niches]:
            return f"{desired_niche}_hyper_niche"
        return desired_niche
        
    def calculate_saturation(self, niche: str, existing_niches: List[str]) -> float:
        """Saturation scoring based on existing overlapping channels."""
        count = sum(1 for n in existing_niches if niche.lower() in n.lower())
        return float(min(100, count * 20))
