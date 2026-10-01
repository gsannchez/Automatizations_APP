"""Retention Estimator service for predicting viewer retention rate curve."""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class RetentionEstimator:
    """Predicts how long viewers will stay on the video based on script syntax and length."""
    
    def estimate_retention(self, hook_score: float, script_text: str, scene_durations: List[float]) -> Dict[str, Any]:
        """Generate a simulated retention curve and average retention score.
        
        Args:
            hook_score: Precalculated score of the hook phase.
            script_text: Full voiceover text.
            scene_durations: List of durations in seconds for each scene.
            
        Returns:
            Dict containing average_retention and retention_curve points.
        """
        if not script_text or not scene_durations:
            return {"average_retention": 0.0, "retention_curve": {}}
            
        total_duration = sum(scene_durations)
        words_count = len(script_text.split())
        
        # Heuristics:
        # 1. Total length penalty: shorter videos (15-40s) have naturally higher retention rate
        length_factor = 1.0
        if total_duration > 60:
            length_factor = 0.55
        elif total_duration > 40:
            length_factor = 0.75
        elif total_duration > 25:
            length_factor = 0.90
            
        # 2. Scene variance penalty: irregular scene lengths reduce retention
        import numpy as np
        if len(scene_durations) > 1:
            duration_std = float(np.std(scene_durations))
            pacing_variance_penalty = max(0.0, min(duration_std * 0.05, 0.20))
        else:
            pacing_variance_penalty = 0.15
            
        # Base retention calculation
        base_retention = (hook_score * 0.45) + (length_factor * 0.40) - pacing_variance_penalty
        average_retention = max(0.15, min(base_retention + 0.15, 0.95))
        
        # 3. Build retention curve (simulated percentage stay at 0s, 3s, 10s, 30s, 60s)
        # Drop-off is steepest in the first 3 seconds (governed by hook score)
        retention_3s = 0.95 if hook_score > 0.8 else (0.60 + hook_score * 0.35)
        retention_10s = retention_3s * 0.85
        retention_30s = retention_10s * (0.75 if total_duration > 30 else 0.90)
        retention_end = retention_30s * (0.50 if total_duration > 60 else 0.80)
        
        curve = {
            "0s": 1.0,
            "3s": round(retention_3s, 2),
            "10s": round(retention_10s, 2),
            "30s": round(retention_30s, 2),
            "end": round(retention_end, 2)
        }
        
        return {
            "average_retention": round(average_retention, 2),
            "retention_curve": curve,
            "total_duration": total_duration,
            "words_count": words_count
        }
