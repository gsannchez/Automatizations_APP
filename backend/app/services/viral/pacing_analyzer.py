"""Pacing Analyzer service for voiceover text and scene timing."""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PacingAnalyzer:
    """Analyzes the speed of narration and scene-to-scene variations."""
    
    def analyze_pacing(self, script_text: str, scene_durations: List[float]) -> Dict[str, Any]:
        """Compute words per second (WPS) and scene rhythm.
        
        Args:
            script_text: Full voiceover script.
            scene_durations: List of durations in seconds for each scene.
            
        Returns:
            Dict containing pacing_score, wps, and formatting advice.
        """
        if not script_text or not scene_durations:
            return {"pacing_score": 0.0, "wps": 0.0, "feedback": "Missing script text or scene durations."}
            
        words = script_text.split()
        words_count = len(words)
        total_duration = sum(scene_durations)
        
        if total_duration == 0:
            return {"pacing_score": 0.0, "wps": 0.0}
            
        # 1. Words Per Second (WPS)
        wps = words_count / total_duration
        
        # Ideal social media pacing: between 2.2 and 3.2 words per second.
        # Below 2.0 is too slow (boring). Above 3.8 is too fast (unintelligible).
        if 2.2 <= wps <= 3.2:
            wps_score = 1.0
        elif wps < 2.2:
            wps_score = max(0.2, 1.0 - (2.2 - wps) * 0.8)
        else:
            wps_score = max(0.2, 1.0 - (wps - 3.2) * 0.8)
            
        # 2. Scene transitions rate
        # Ideal scene duration is between 3 and 7 seconds. Less than 2 is too jumpy, more than 8 is too slow.
        scene_scores = []
        for dur in scene_durations:
            if 3.0 <= dur <= 7.0:
                scene_scores.append(1.0)
            elif dur < 3.0:
                scene_scores.append(0.6)
            else:
                scene_scores.append(max(0.1, 1.0 - (dur - 7.0) * 0.15))
                
        avg_scene_score = sum(scene_scores) / len(scene_scores) if scene_scores else 0.0
        
        # Combined score
        pacing_score = (wps_score * 0.6) + (avg_scene_score * 0.4)
        
        # Formulate feedback
        feedback = ""
        if wps < 2.0:
            feedback = "Ritmo demasiado lento. Añade más texto o reduce la duración global de las escenas."
        elif wps > 3.6:
            feedback = "Ritmo demasiado acelerado. Elimina palabras del guion o incrementa la duración de las escenas para respiración."
        else:
            feedback = "Rango de locución perfecto. Ritmo altamente dinámico adecuado para retención en redes."
            
        return {
            "pacing_score": round(pacing_score, 2),
            "wps": round(wps, 2),
            "avg_scene_duration": round(total_duration / len(scene_durations), 2) if scene_durations else 0.0,
            "feedback": feedback
        }
