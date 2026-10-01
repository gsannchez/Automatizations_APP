from typing import List
from datetime import datetime
from ...models.viral_intelligence import TrendingTopic

class TrendRanker:
    """Ranks trending topics based on velocity, reuse count, and recency."""

    @staticmethod
    def get_top(trends: List[TrendingTopic], top_n: int = 5) -> List[TrendingTopic]:
        """
        Ranks trends using the formula:
        score = (velocity * 0.4) + (reuse_count * 0.3) + (recency * 0.3)
        """
        if not trends:
            return []

        # Find max values for normalization
        max_velocity = max((t.velocity_score for t in trends), default=1.0) or 1.0
        max_reuse = max((t.reuse_count for t in trends), default=1) or 1
        
        now = datetime.utcnow()
        ranked_trends = []

        for t in trends:
            # Normalize inputs to 0-1
            norm_vel = t.velocity_score / max_velocity
            norm_reuse = t.reuse_count / max_reuse
            
            # Recency: 1.0 if seen just now, decays linearly over 7 days
            days_old = (now - t.last_seen).total_seconds() / 86400.0
            norm_recency = max(0.0, 1.0 - (days_old / 7.0))

            # Apply formula
            score = (norm_vel * 0.4) + (norm_reuse * 0.3) + (norm_recency * 0.3)
            ranked_trends.append((score, t))

        # Sort descending by score
        ranked_trends.sort(key=lambda x: x[0], reverse=True)
        return [t for score, t in ranked_trends[:top_n]]
