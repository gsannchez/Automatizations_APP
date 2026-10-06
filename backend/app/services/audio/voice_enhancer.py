class VoiceEnhancer:
    """
    Enhances voice tracks (TTS or human) using FFmpeg audio filters.
    Applies normalization, light compression, and basic EQ.
    """

    #: EBU R128 integrated loudness target. Must match the final-mix target in
    #: ``services/ai/video_generation/timeline.py`` — if the two disagree, the
    #: second ``loudnorm`` pass fights the first and the voice audibly pumps.
    TARGET_LUFS = -14

    @staticmethod
    def get_enhancement_filter(target_lufs: float = TARGET_LUFS) -> str:
        """
        Returns an FFmpeg audio filter string for voice enhancement.
        - highpass: removes low rumble
        - acompressor: light compression to even out volume
        - loudnorm: EBU R128 loudness normalization
        """
        return (
            "highpass=f=80,"
            "acompressor=threshold=-15dB:ratio=3:attack=5:release=50,"
            f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11"
        )
