class CinematicFilters:
    """
    Applies color grading, grain, vignette, etc. depending on the style.
    """
    
    @staticmethod
    def get_filter_string(style: str) -> str:
        """
        Returns a chain of video filters (e.g., 'eq=contrast=1.1:saturation=1.2,vignette=PI/4')
        """
        style = style.lower()
        
        if "cctv" in style:
            # Grayscale, high contrast, noise/grain
            return "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3,eq=contrast=1.5:brightness=-0.1,noise=alls=50:allf=t+u"
        elif "horror" in style:
            # Dark, desaturated, slight green tint
            return "eq=contrast=1.2:brightness=-0.2:saturation=0.5:gamma_g=1.1,vignette=PI/3"
        elif "cinematic" in style:
            # High contrast, slight teal/orange shift
            return "eq=contrast=1.1:saturation=1.1,vignette=PI/4"
        elif "tiktok" in style:
            # Bright, high saturation
            return "eq=contrast=1.05:brightness=0.05:saturation=1.3"
        else:
            return "" # Pass-through
