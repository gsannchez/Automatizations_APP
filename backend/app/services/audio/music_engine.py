import os
import random

class MusicEngine:
    """
    Selects and manages background music tracks based on the visual style/profile.
    """
    MUSIC_LIBRARY = {
        "tiktok_classic": ["media/resources/audio/upbeat_1.mp3", "media/resources/audio/viral_beat.mp3"],
        "cinematic": ["media/resources/audio/epic_orchestral.mp3", "media/resources/audio/tension.mp3"],
        "cctv": ["media/resources/audio/dark_ambient.mp3", "media/resources/audio/drone.mp3"],
        "meme": ["media/resources/audio/funny_flute.mp3", "media/resources/audio/derp.mp3"]
    }

    @staticmethod
    def select_background_music(style_name: str) -> str:
        """
        Returns a local path to a suitable background music track.
        """
        # Map generic style to a music category
        category = "tiktok_classic"
        style_lower = style_name.lower()
        if "cinematic" in style_lower or "documentary" in style_lower:
            category = "cinematic"
        elif "cctv" in style_lower or "horror" in style_lower:
            category = "cctv"
        elif "meme" in style_lower or "funny" in style_lower:
            category = "meme"
            
        tracks = MusicEngine.MUSIC_LIBRARY.get(category, MusicEngine.MUSIC_LIBRARY["tiktok_classic"])
        selected = random.choice(tracks)
        
        # In a real scenario, you'd download from storage if not local.
        # Here we just return the path (assuming it exists or will be handled by the pipeline)
        return selected

    @staticmethod
    def get_music_filter(volume: float = 0.2) -> str:
        """
        Base volume adjustment for music before ducking.
        """
        return f"volume={volume}"
