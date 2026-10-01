class DuckingEngine:
    """
    Generates FFmpeg filter complex graphs for audio ducking
    (lowering background music volume when someone is speaking).
    """
    
    @staticmethod
    def get_ducking_filter_graph(voice_stream: str, music_stream: str, out_stream: str) -> str:
        """
        Creates a sidechain compression filter to duck the music_stream based on the voice_stream.
        
        Args:
            voice_stream: The label of the voice stream, e.g., '[0:a]'
            music_stream: The label of the music stream, e.g., '[1:a]'
            out_stream: The label for the mixed output, e.g., '[aout]'
            
        Returns:
            A string containing the FFmpeg filter complex for ducking and mixing.
        """
        # 1. Split voice into two: one for the mix, one for the sidechain trigger
        # 2. Apply sidechaincompress to the music using the second voice stream
        # 3. Mix the sidechained music and the first voice stream
        
        graph = (
            f"{voice_stream}asplit=2[v_mix][v_sc]; "
            f"{music_stream}[v_sc]sidechaincompress=threshold=0.05:ratio=4:attack=50:release=200[m_ducked]; "
            f"[v_mix][m_ducked]amix=inputs=2:duration=first:dropout_transition=2{out_stream}"
        )
        return graph
