import os
import uuid
from typing import Optional
from .word_timing import WordTimingEngine
from .animated_captions import AnimatedCaptionsEngine
from .caption_styles import CaptionStyleProfile

class CaptionGenerator:
    """
    Main entry point for generating dynamic captions for a scene.
    """
    def __init__(self, tmp_dir: str):
        self.tmp_dir = tmp_dir
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, exist_ok=True)

    def generate_captions(self, text: str, audio_duration: float, profile: CaptionStyleProfile = CaptionStyleProfile.TIKTOK_CLASSIC) -> Optional[str]:
        """
        Generates an ASS subtitle file for the given text and audio duration.
        Returns the local path to the generated .ass file.
        """
        if not text.strip():
            return None

        # 1. Estimate word timings
        timings = WordTimingEngine.estimate_word_timings(text, audio_duration)
        
        # 2. Generate ASS file
        output_filename = f"captions_{uuid.uuid4().hex[:8]}.ass"
        output_path = os.path.join(self.tmp_dir, output_filename)
        
        AnimatedCaptionsEngine.generate_ass_file(timings, profile, output_path)
        
        return output_path
