from .voice_enhancer import VoiceEnhancer
from .music_engine import MusicEngine
from .ducking_engine import DuckingEngine

class AudioMixer:
    """
    Orchestrates the entire audio pipeline for the final video.
    Combines voice enhancement, music selection, and ducking into a single filter graph.
    """
    
    @staticmethod
    def build_audio_pipeline(voice_input_idx: int, music_input_idx: int, bg_volume: float = 0.2) -> str:
        """
        Builds the FFmpeg filter_complex string for mixing voice and music.
        Assumes voice is at input index voice_input_idx, and music at music_input_idx.
        """
        voice_stream = f"[{voice_input_idx}:a]"
        music_stream = f"[{music_input_idx}:a]"
        
        # 1. Enhance Voice
        enhancement = VoiceEnhancer.get_enhancement_filter()
        
        # 2. Base Volume for Music
        music_vol = MusicEngine.get_music_filter(volume=bg_volume)
        
        # 3. Ducking Graph
        # Voice: [v_in] -> enhance -> [v_enh]
        # Music: [m_in] -> volume -> [m_vol]
        # Duck: [v_enh] + [m_vol] -> [aout]
        
        filter_str = (
            f"{voice_stream}{enhancement}[v_enh]; "
            f"{music_stream}{music_vol}[m_vol]; "
        )
        
        ducking = DuckingEngine.get_ducking_filter_graph("[v_enh]", "[m_vol]", "[aout]")
        filter_str += ducking
        
        return filter_str
