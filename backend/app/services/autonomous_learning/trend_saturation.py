from enum import Enum
from datetime import datetime
from ...models.viral_intelligence import TrendingTopic

class SaturationState(str, Enum):
    FRESH = "FRESH"
    GROWING = "GROWING"
    PEAK = "PEAK"
    SATURATED = "SATURATED"
    DEAD = "DEAD"

class TrendSaturationDetector:
    """Detects saturation of viral trends."""
    
    @staticmethod
    def detect(trend: TrendingTopic) -> SaturationState:
        age_days = (datetime.utcnow() - trend.created_at).total_seconds() / 86400.0
        
        if trend.reuse_count > 5000 or (age_days > 30 and trend.velocity_score < 20):
            return SaturationState.DEAD
        if trend.reuse_count > 2000 or trend.velocity_score < 40:
            return SaturationState.SATURATED
        if trend.velocity_score > 80 and trend.reuse_count > 500:
            return SaturationState.PEAK
        if trend.velocity_score > 60:
            return SaturationState.GROWING
            
        return SaturationState.FRESH
