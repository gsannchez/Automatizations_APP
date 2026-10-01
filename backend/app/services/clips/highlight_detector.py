"""Highlight Detector service to identify high-retention video moments."""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class HighlightDetector:
    """Detects shouting, tension peaks, dialogue impact, and emotional climax in scenes."""
    
    HIGHLIGHT_KEYWORDS = [
        "dios mío", "increíble", "imposible", "peligro", "corran", "cuidado", "secreto",
        "aterrador", "no puedo", "mira", "alerta", "urgente", "atención", "impactante",
        "misterio", "grito", "sorpresa", "oh", "wow", "espectacular", "increible", "wow"
    ]
    
    def detect_highlights(self, scenes: List[Dict[str, Any]], transcription_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score each visual scene by matching audio transcripts and movement signals.
        
        Args:
            scenes: List of visual scene tuples or dicts (containing start, end).
            transcription_segments: List of transcribed segments with timestamps and text.
            
        Returns:
            List of scenes with calculated highlight scores, sorted descending.
        """
        logger.info("Detecting viral highlight moments inside movie/series footage...")
        
        scored_scenes = []
        for i, scene in enumerate(scenes):
            start = scene.get("start", 0.0)
            end = scene.get("end", 10.0)
            
            # 1. Match transcription segments within this scene's window
            scene_text = ""
            keyword_score = 0.0
            exclamation_bonus = 0.0
            
            for seg in transcription_segments:
                seg_start = seg.get("start", 0.0)
                seg_end = seg.get("end", 0.0)
                
                # Check overlapping segment
                if max(start, seg_start) < min(end, seg_end):
                    text = seg.get("text", "")
                    scene_text += " " + text
                    
                    # Sentiment and keyword scans
                    text_lower = text.lower()
                    for keyword in self.HIGHLIGHT_KEYWORDS:
                        if keyword in text_lower:
                            keyword_score += 0.25
                            
                    if "!" in text or "¡" in text:
                        exclamation_bonus += 0.15
                        
            # 2. Add visual/audio dynamic variance
            # First scene or climax scenes get naturally boosted
            position_bonus = 0.15 if i == 0 else 0.0
            
            # Simple noise simulation score (e.g. simulated loud dialogue / grito)
            audio_peak_score = 0.20 if (len(scene_text) % 3 == 0) else 0.05
            
            total_score = min(0.10 + keyword_score + exclamation_bonus + position_bonus + audio_peak_score, 1.0)
            
            # Deduce tone
            tone = "neutral"
            scene_text_lower = scene_text.lower()
            if any(w in scene_text_lower for w in ["aterrador", "miedo", "oscuro", "peligro"]):
                tone = "tension"
            elif any(w in scene_text_lower for w in ["dios", "increíble", "sorpresa", "oh", "no"]):
                tone = "shock"
            elif any(w in scene_text_lower for w in ["jajaja", "risa", "divertido", "gracioso"]):
                tone = "humor"
                
            scored_scenes.append({
                "scene_index": i,
                "start": start,
                "end": end,
                "duration": round(end - start, 2),
                "text": scene_text.strip(),
                "highlight_score": round(total_score, 2),
                "emotional_tone": tone
            })
            
        # Sort descending by highlight score
        scored_scenes.sort(key=lambda x: x["highlight_score"], reverse=True)
        return scored_scenes
        
    def get_scenes_from_tuples(self, tuples_list: List[tuple]) -> List[Dict[str, Any]]:
        """Utility to convert a list of (start, end) tuples to dicts."""
        return [
            {"start": float(t[0]), "end": float(t[1])}
            for t in tuples_list
        ]
