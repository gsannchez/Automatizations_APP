class ExportOptimizer:
    """
    Ensures the final output meets specific platform requirements 
    (TikTok, Reels, Shorts).
    """
    
    @staticmethod
    def get_ffmpeg_export_args() -> list:
        """
        Returns a list of FFmpeg arguments optimized for TikTok/Reels.
        - 1080x1920
        - 30 fps
        - H.264, yuv420p
        - AAC audio, 192k
        """
        return [
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart"
        ]
