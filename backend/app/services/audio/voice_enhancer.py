class VoiceEnhancer:
    """
    Enhances voice tracks (TTS or human) using FFmpeg audio filters.
    Applies normalization, light compression, and basic EQ.
    """
    @staticmethod
    def get_enhancement_filter() -> str:
        """
        Returns an FFmpeg audio filter string for voice enhancement.
        - loudnorm: EBU R128 loudness normalization
        - acompressor: light compression to even out volume
        - highpass: removes low rumble
        """
        return "highpass=f=80,acompressor=threshold=-15dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1.5:LRA=11"
