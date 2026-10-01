class EmergencyFallback:
    """
    Returns a mocked or FFmpeg-based fallback when AI video fails completely.
    """
    @staticmethod
    def get_fallback_video(*args, **kwargs) -> dict:
        """
        Returns a dictionary signaling that AI video failed, 
        and the system should revert to static image + FFmpeg zoom.
        """
        # Normally this would return a pre-rendered static clip or modify the scene params.
        # We simulate returning a flag to use FFmpeg fallback.
        return {
            "is_ai_video": False,
            "video_path": None,
            "fallback_used": True
        }
