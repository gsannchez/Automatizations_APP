from typing import List, Dict

class PacingAnalyzer:
    """
    Analyzes the pacing of the video. Ensures that no scene is too long
    without some form of visual change (cut, aggressive zoom, etc.).
    """
    
    # Max duration in seconds before a mandatory visual change
    MAX_SCENE_DURATION_TIKTOK = 3.0
    MAX_SCENE_DURATION_CINEMATIC = 4.5
    
    @staticmethod
    def needs_rebalance(scenes: List[Dict], style: str = "tiktok") -> bool:
        """
        Returns True if any scene exceeds the max duration for the given style.
        """
        max_dur = PacingAnalyzer.MAX_SCENE_DURATION_CINEMATIC if "cinematic" in style.lower() else PacingAnalyzer.MAX_SCENE_DURATION_TIKTOK
        
        for scene in scenes:
            dur = scene.get("duration", 0)
            if dur > max_dur:
                return True
                
        return False
