from dataclasses import dataclass
from typing import List, Dict, Any
from sqlmodel import Session, select
from ...models.viral_intelligence import VideoPerformanceMetrics

@dataclass
class PerformanceInsight:
    winning_hooks: List[str]
    failing_hooks: List[str]
    best_styles: List[str]
    best_durations: List[int]
    engagement_drop_patterns: List[str]
    saturation_risk: Dict[str, float]

class PerformanceFeedbackEngine:
    """Analyzes historical video metrics and extracts patterns."""
    
    def __init__(self, session: Session):
        self.session = session
        
    def analyze_history(self) -> PerformanceInsight:
        metrics = self.session.execute(
            select(VideoPerformanceMetrics).order_by(VideoPerformanceMetrics.views.desc()).limit(100)
        ).scalars().all()
        
        if not metrics:
            return PerformanceInsight([], [], [], [], [], {})
            
        winning_hooks = ["This secret changes everything..."] # Placeholder logic
        failing_hooks = ["In this video I will show you..."] 
        
        styles = {}
        for m in metrics:
            # We would join with Video -> TrendingTopic to get exact style, here mocked
            pass
            
        return PerformanceInsight(
            winning_hooks=winning_hooks,
            failing_hooks=failing_hooks,
            best_styles=["BODYCAM", "TIKTOK_NATIVE"],
            best_durations=[30, 45],
            engagement_drop_patterns=["Drop at 3s if no motion"],
            saturation_risk={"dog rescue": 0.2, "crime footage": 0.8}
        )
