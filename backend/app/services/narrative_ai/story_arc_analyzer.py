"""
app/services/narrative_ai/story_arc_analyzer.py

Phase 10: Master coordinator for Narrative Intelligence.
"""
import logging
from typing import Dict, Any, List

from .narrative_modules import (
    EmotionalCurveAnalyzer,
    HookStrengthEvaluator,
    TensionTracker,
    PacingEvaluator,
    NarrativeCoherence
)

logger = logging.getLogger(__name__)

class StoryArcAnalyzer:
    def __init__(self):
        self.emotion = EmotionalCurveAnalyzer()
        self.hook = HookStrengthEvaluator()
        self.tension = TensionTracker()
        self.pacing = PacingEvaluator()
        self.coherence = NarrativeCoherence()

    def analyze_script(self, script_scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidates narrative metrics to generate a final narrative_score 
        and retention_prediction.
        """
        logger.info(f"[StoryArcAnalyzer] Analyzing {len(script_scenes)} scenes for narrative arc.")
        
        emotion_data = self.emotion.analyze(script_scenes)
        hook_score = self.hook.evaluate(script_scenes)
        tension_score = self.tension.measure(emotion_data["curve"])
        pacing_data = self.pacing.evaluate(script_scenes)
        coherence_score = self.coherence.evaluate(script_scenes)
        
        # Weighted narrative score
        narrative_score = (
            (hook_score * 0.3) +
            (min(100.0, tension_score) * 0.2) +
            ((100 - (len(pacing_data["alerts"]) * 10)) * 0.3) +
            (coherence_score * 0.2)
        )
        
        # Retention prediction (heuristic mapping)
        retention_prediction = narrative_score * 0.85 
        
        return {
            "narrative_score": round(narrative_score, 2),
            "retention_prediction": round(retention_prediction, 2),
            "pacing_alerts": pacing_data["alerts"],
            "emotional_graph": emotion_data["curve"],
            "metrics": {
                "hook_strength": hook_score,
                "tension": tension_score,
                "coherence": coherence_score,
                "average_scene_duration": pacing_data["average_scene_duration"]
            }
        }
