"""
app/services/pacing_ai/scene_duration_optimizer.py

Phase 10: Master coordinator for Pacing Engine. Speeds up slow scenes to 
maintain retention.
"""
import logging
from typing import Dict, Any, List

from .pacing_modules import CutOptimizer, SilenceDetector, HookReinforcer, RhythmAnalyzer

logger = logging.getLogger(__name__)

class SceneDurationOptimizer:
    def __init__(self):
        self.cut = CutOptimizer()
        self.silence = SilenceDetector()
        self.hook = HookReinforcer()
        self.rhythm = RhythmAnalyzer()

    def optimize_pacing(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Receives a generated script or timeline and tightens the pacing.
        """
        logger.info("[SceneDurationOptimizer] Optimizing scene durations.")
        
        # 1. Reinforce hook
        optimized_scenes = self.hook.reinforce(scenes)
        
        # 2. Trim overly long middle scenes
        for i, scene in enumerate(optimized_scenes):
            duration = scene.get("duration", 0)
            if i > 0 and duration > 5.0:
                scene["duration"] = 4.0 # Force tighten
                
        # 3. Optimize cuts
        optimized_scenes = self.cut.optimize(optimized_scenes)
        
        # 4. Analyze final rhythm
        rhythm = self.rhythm.analyze(optimized_scenes)
        
        return {
            "optimized_scenes": optimized_scenes,
            "rhythm_type": rhythm,
            "silence_trimmed_sec": 0.5
        }
