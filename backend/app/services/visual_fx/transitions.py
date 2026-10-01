class TransitionsEngine:
    """
    Handles transitions between scenes. 
    Note: In advanced FFmpeg pipelines, using `xfade` across many clips 
    requires a cascading filter_complex graph.
    """
    
    @staticmethod
    def get_xfade_filter(transition_type: str = "fade", duration: float = 0.5, offset: float = 0.0) -> str:
        """
        Helper to generate an xfade filter string.
        Available types: fade, wipeleft, wiperight, slideleft, slideright, circlecrop, rectcrop, distance, fadeblack, fadewhite, radial, smoothleft, smoothright, smoothup, smoothdown, circleopen, circleclose, vertopen, vertclose, horzopen, horzclose, dissolve, pixelize, diagbl, diagbr, diagtl, diagtr, hlslice, hrslice, vuslice, vdslice.
        """
        return f"xfade=transition={transition_type}:duration={duration}:offset={offset}"
