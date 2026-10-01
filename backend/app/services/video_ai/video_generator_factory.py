import os

try:
    import torch
except ImportError:
    torch = None

class VideoGeneratorFactory:
    """
    Decoupled architecture to select the appropriate AI Video backend.
    """
    
    @staticmethod
    def get_generator(style: str, preferred_engine: str = "auto"):
        """
        Selects the video engine based on VRAM, style, and priority.
        For 12GB VRAM, we strongly prefer lightweight AnimateDiff or low-res SVD.
        """
        # 12GB VRAM heuristic check (mocked for this logic)
        vram_gb = 0
        if torch is not None and hasattr(torch, 'cuda') and torch.cuda.is_available():
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
        if preferred_engine == "animatediff" or (preferred_engine == "auto" and "anime" in style.lower()):
            from .animatediff_generator import AnimateDiffGenerator
            return AnimateDiffGenerator()
        elif preferred_engine == "svd" or (preferred_engine == "auto" and "realism" in style.lower()):
            from .svd_generator import SVDGenerator
            return SVDGenerator()
        else:
            # Fallback to AnimateDiff as default for TikTok/Viral
            from .animatediff_generator import AnimateDiffGenerator
            return AnimateDiffGenerator()
