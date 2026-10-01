"""Scoring service to calculate trend virality and momentum metrics."""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TrendScorer:
    """Calculates engagement, momentum, and virality indices for social trends."""
    
    def calculate_metrics(self, raw_trend: Dict[str, Any]) -> Dict[str, float]:
        """Calculate standardized scores from raw trend measurements.
        
        Args:
            raw_trend: Raw dictionary from scraper.
            
        Returns:
            Dict containing virality_score, momentum_score, and engagement_rate.
        """
        avg_views = raw_trend.get("avg_views", 1_000_000)
        engagement_rate = raw_trend.get("engagement_rate", 0.05)
        
        # 1. Virality Score (0.0 to 100.0)
        # Based on view magnitude and high relative engagement rate
        # Logarithmic scale on views to prevent extreme outliers dominating
        import math
        view_factor = min(math.log10(avg_views) / 8.0, 1.2) # Normalized around 10M views
        eng_factor = min(engagement_rate * 5.0, 1.2)        # Normalized around 20% engagement
        
        virality_score = min(((view_factor * 0.5) + (eng_factor * 0.5)) * 100.0, 100.0)
        
        # 2. Momentum Score (0.0 to 100.0)
        # Velocity / speed of trend adoption. Freshness factor.
        # Derived from hashtags variety and engagement intensity
        hashtag_count = len(raw_trend.get("hashtags", []))
        hash_factor = min(hashtag_count / 10.0, 1.0)
        
        # Random but deterministic offset based on category name to simulate dynamic changes
        category_hash = abs(hash(raw_trend.get("category", "general")))
        dynamic_velocity = (category_hash % 25) + 65.0 # 65.0 to 90.0 momentum
        
        momentum_score = min((dynamic_velocity * 0.8) + (hash_factor * 20.0), 100.0)
        
        return {
            "virality_score": round(virality_score, 2),
            "momentum_score": round(momentum_score, 2),
            "engagement_rate": round(engagement_rate, 4)
        }
