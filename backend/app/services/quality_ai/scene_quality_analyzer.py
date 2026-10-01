"""
app/services/quality_ai/scene_quality_analyzer.py

Phase 10: Central coordinator for all scene quality checks.
Runs deterministic heuristics first, falling back to optional ML models.
"""
import logging
from typing import Dict, Any

from .deterministic_detectors import BlurDetector, FlickerDetector, FrameConsistencyAnalyzer, MotionScorer
from .ml_detectors import RealismDetector, ArtifactDetector

logger = logging.getLogger(__name__)

class SceneQualityAnalyzer:
    def __init__(self):
        self.blur_detector = BlurDetector()
        self.flicker_detector = FlickerDetector()
        self.artifact_detector = ArtifactDetector()
        self.motion_scorer = MotionScorer()
        self.realism_detector = RealismDetector()
        self.consistency = FrameConsistencyAnalyzer()

    async def evaluate_video(self, video_path: str) -> Dict[str, Any]:
        """
        Extracts frames and runs the cascade of quality checks.
        Returns a final score and regeneration recommendation.
        """
        logger.info(f"[SceneQualityAnalyzer] Evaluating {video_path}")
        
        # 1. Fast deterministic checks
        blur_score = self.blur_detector.analyze(video_path)
        flicker_score = self.flicker_detector.analyze(video_path)
        
        failure_reasons = {}
        if blur_score < 40.0:
            failure_reasons["motion_blur"] = blur_score
        if flicker_score > 60.0:
            failure_reasons["flicker"] = flicker_score
            
        # 2. Heuristic temporal checks
        motion_score = self.motion_scorer.analyze(video_path)
        consistency_score = self.consistency.analyze(video_path)
        
        if motion_score < 30.0:
            failure_reasons["poor_motion"] = motion_score
        if consistency_score < 50.0:
            failure_reasons["temporal_instability"] = consistency_score
            
        # 3. Optional Deep Learning checks (mocked for safety/speed by default)
        artifact_score = self.artifact_detector.analyze(video_path)
        realism_score = self.realism_detector.analyze(video_path)
        
        if artifact_score > 50.0:
            failure_reasons["artifacting"] = artifact_score
        if realism_score < 40.0:
            failure_reasons["warped_face"] = realism_score
            
        # Calculate Final Score
        metrics = {
            "blur": blur_score,
            "flicker": flicker_score,
            "motion": motion_score,
            "consistency": consistency_score,
            "artifacts": artifact_score,
            "realism": realism_score
        }
        
        overall_score = sum(metrics.values()) / len(metrics) # Simplified
        
        # Determine Enum Status
        if len(failure_reasons) > 2 or any(v < 20 for v in [blur_score, motion_score, realism_score]):
            status = "CRITICAL"
        elif failure_reasons:
            status = "LOW"
        elif overall_score > 85:
            status = "EXCELLENT"
        elif overall_score > 70:
            status = "GOOD"
        else:
            status = "ACCEPTABLE"
            
        return {
            "score": status,
            "metrics": metrics,
            "failure_reasons": failure_reasons,
            "regeneration_recommended": status in ["CRITICAL", "LOW"]
        }
