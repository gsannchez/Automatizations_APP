class AttentionGrabber:
    """
    Ensures the first 2 seconds have maximum impact.
    Adds a 'swoosh' or 'impact' sound effect, and perhaps a fast visual zoom.
    """
    
    @staticmethod
    def get_hook_sfx() -> str:
        """
        Returns the local path to a hook sound effect.
        """
        return "media/resources/audio/sfx_impact.mp3"
        
    @staticmethod
    def get_hook_visual_filter() -> str:
        """
        Returns a high-energy visual filter for the first few seconds (e.g., flash or fast zoom).
        This would be prepended or combined with the first scene's filter.
        """
        # A quick zoom out that stops
        return "zoompan=z='if(lte(time,1),max(1.5-time*0.5,1.0),1.0)':d=100:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
