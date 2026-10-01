class MotionScheduler:
    """
    Decides how much motion a scene should have based on narrative importance
    and emotional context.
    """
    
    @staticmethod
    def calculate_motion_intensity(scene_index: int, style: str, emotion: str = "neutral") -> float:
        """
        Returns a float between 0.0 (static) and 1.0 (chaotic motion).
        """
        intensity = 0.5
        
        # Hooks get more motion
        if scene_index == 0:
            intensity += 0.3
            
        style_lower = style.lower()
        if "meme" in style_lower:
            intensity += 0.4
        elif "cctv" in style_lower:
            intensity -= 0.4
        elif "cinematic" in style_lower:
            intensity -= 0.1 # Slower, deliberate motion
            
        if emotion in ["shock", "anger", "excitement"]:
            intensity += 0.2
        elif emotion in ["sadness", "calm"]:
            intensity -= 0.2
            
        return max(0.0, min(1.0, intensity))
        
    @staticmethod
    def requires_ai_video(intensity: float, style: str) -> bool:
        """
        Heuristic to decide if this scene warrants expensive AI generation,
        or if FFmpeg static motion is enough.
        """
        if "cctv" in style.lower():
            return False # CCTV is mostly static, FFmpeg is fine
        if intensity > 0.6:
            return True
        return False
