from .quality_manager import QualityManager, QualityTier

class AdaptiveRendering:
    """
    Adjusts FFmpeg and AI video parameters based on the current quality tier.
    """
    @staticmethod
    def get_render_params() -> dict:
        tier = QualityManager.get_tier()
        
        params = {
            "fps": 30,
            "crf": 23,
            "preset": "fast",
            "allow_ai_video": True
        }
        
        if tier == QualityTier.ULTRA:
            params["fps"] = 60
            params["crf"] = 18
            params["preset"] = "medium"
        elif tier == QualityTier.BALANCED:
            params["crf"] = 28
        elif tier == QualityTier.PERFORMANCE:
            params["fps"] = 24
            params["crf"] = 32
            params["preset"] = "veryfast"
            params["allow_ai_video"] = False
        elif tier == QualityTier.SAFE_MODE:
            params["fps"] = 24
            params["crf"] = 35
            params["preset"] = "ultrafast"
            params["allow_ai_video"] = False
            
        return params
