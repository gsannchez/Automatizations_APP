import logging

logger = logging.getLogger(__name__)

class WorkloadEstimator:
    """
    Predicts VRAM and execution time for tasks to aid in scheduling.
    """
    
    # Baseline heuristics (would ideally come from ML models based on past metrics)
    VRAM_ESTIMATES = {
        "sdxl_generation": 8000, # 8GB
        "flux_generation": 12000, # 12GB
        "whisper_transcription": 4000, # 4GB
        "ffmpeg_render": 2000, # 2GB
        "ai_video_generation": 16000 # 16GB
    }

    TIME_ESTIMATES = {
        "sdxl_generation": 15.0, # seconds
        "flux_generation": 25.0,
        "whisper_transcription": 10.0, # base seconds, scale with duration
        "ffmpeg_render": 30.0,
        "ai_video_generation": 120.0
    }

    @classmethod
    def estimate_vram(cls, task_type: str, quality_tier: str = "high") -> int:
        """Estimate VRAM footprint in MB."""
        base_vram = cls.VRAM_ESTIMATES.get(task_type, 4000)
        
        # Adjust for quality tier
        if quality_tier == "low":
            return int(base_vram * 0.6)
        elif quality_tier == "medium":
            return int(base_vram * 0.8)
            
        return base_vram

    @classmethod
    def estimate_duration(cls, task_type: str, input_size_units: float = 1.0) -> float:
        """Estimate duration in seconds, scaled by input size (e.g., video length)."""
        base_time = cls.TIME_ESTIMATES.get(task_type, 20.0)
        return base_time * input_size_units
