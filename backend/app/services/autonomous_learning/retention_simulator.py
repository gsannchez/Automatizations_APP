from dataclasses import dataclass
from typing import List

@dataclass
class RetentionSimulation:
    predicted_drop_points: List[float]
    estimated_completion_rate: float
    hook_strength: float
    pacing_score: float

class RetentionSimulator:
    """Simulates retention before render."""
    
    @classmethod
    def simulate(cls, scenes: List[dict], hook_score: float) -> RetentionSimulation:
        """Heuristic analysis of scene lengths, pacing, repetition."""
        if not scenes:
            return RetentionSimulation([], 0.0, 0.0, 0.0)
            
        total_duration = sum(s.get("duration", 5.0) for s in scenes)
        drop_points = []
        pacing_issues = 0
        
        # Analyze pacing
        for i, s in enumerate(scenes):
            dur = s.get("duration", 5.0)
            if dur > 6.0:
                pacing_issues += 1
                drop_points.append(sum(x.get("duration", 5.0) for x in scenes[:i+1]))
                
        pacing_score = max(0.0, 100.0 - (pacing_issues * 15))
        
        # Estimate completion
        base_completion = 0.5 + (hook_score / 200.0)
        penalty = (pacing_issues * 0.05)
        estimated = max(0.0, base_completion - penalty)
        
        return RetentionSimulation(
            predicted_drop_points=drop_points,
            estimated_completion_rate=estimated,
            hook_strength=hook_score,
            pacing_score=pacing_score
        )
