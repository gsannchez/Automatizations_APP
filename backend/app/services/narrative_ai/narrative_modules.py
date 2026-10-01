"""
app/services/narrative_ai/emotional_curve.py
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class EmotionalCurveAnalyzer:
    def analyze(self, script_scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Estimates emotional valence and arousal per scene based on keywords and pacing.
        Returns the data points for an emotional graph.
        """
        graph = []
        valence = 0.0
        for i, scene in enumerate(script_scenes):
            # Heuristic simulation
            text = scene.get("prompt", "").lower() + " " + scene.get("caption", "").lower()
            if any(word in text for word in ["shock", "crazy", "wow", "sudden"]):
                valence += 2.0
            elif any(word in text for word in ["sad", "tragic", "loss"]):
                valence -= 1.5
            else:
                valence += 0.1 # Gentle rise
                
            graph.append({"scene_index": i, "valence": round(valence, 2)})
            
        logger.debug(f"[EmotionalCurveAnalyzer] Generated curve with {len(graph)} points.")
        return {"curve": graph, "final_valence": valence}

"""
app/services/narrative_ai/hook_strength.py
"""
class HookStrengthEvaluator:
    def evaluate(self, script_scenes: List[Dict[str, Any]]) -> float:
        """
        Analyzes the first 3 seconds (typically scenes 0 and 1) for visual and auditory hooks.
        Returns a score 0-100.
        """
        if not script_scenes:
            return 0.0
            
        first_scene = script_scenes[0]
        text = first_scene.get("caption", "").lower()
        prompt = first_scene.get("prompt", "").lower()
        
        score = 50.0 # Base score
        if first_scene.get("duration", 0) < 2.0:
            score += 20.0 # Fast cuts at the start are good
            
        if any(w in text for w in ["wait", "look at", "you won't believe", "secret", "never"]):
            score += 30.0 # Strong text hook
            
        return min(100.0, score)

"""
app/services/narrative_ai/tension_tracker.py
"""
class TensionTracker:
    def measure(self, emotional_graph: List[Dict[str, Any]]) -> float:
        """
        Measures narrative tension by calculating the delta between emotional peaks and troughs.
        """
        if not emotional_graph:
            return 0.0
            
        valences = [p["valence"] for p in emotional_graph]
        tension = max(valences) - min(valences)
        return float(tension * 10) # Scaled heuristic

"""
app/services/narrative_ai/pacing_evaluator.py
"""
class PacingEvaluator:
    def evaluate(self, script_scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detects pacing drops (too many long scenes in a row).
        """
        alerts = []
        consecutive_long_scenes = 0
        
        for i, scene in enumerate(script_scenes):
            if scene.get("duration", 0) > 4.5:
                consecutive_long_scenes += 1
            else:
                consecutive_long_scenes = 0
                
            if consecutive_long_scenes >= 3:
                alerts.append(f"Pacing drop detected starting at scene {i-2}. Too many long scenes.")
                
        # Overall pace
        total_duration = sum(s.get("duration", 0) for s in script_scenes)
        avg_scene = total_duration / len(script_scenes) if script_scenes else 0
        
        return {
            "alerts": alerts,
            "average_scene_duration": round(avg_scene, 2),
            "is_sluggish": len(alerts) > 0
        }

"""
app/services/narrative_ai/narrative_coherence.py
"""
class NarrativeCoherence:
    def evaluate(self, script_scenes: List[Dict[str, Any]]) -> float:
        """
        Checks if scenes follow a logical flow without jarring topical jumps.
        """
        # Mocked semantic coherence check
        return 85.0
