"""
app/services/adaptive_editing/adaptive_editor.py

Phase 10: Coordinates dynamic editing choices just before the final composition phase.
"""
import logging
from typing import Dict, Any

from .editing_modules import (
    EditingStrategySelector,
    DynamicTransitionEngine,
    EmotionBasedEditor,
    MusicSyncEngine,
    BeatAlignmentEngine
)

logger = logging.getLogger(__name__)

class AdaptiveEditor:
    def __init__(self):
        self.strategy = EditingStrategySelector()
        self.transitions = DynamicTransitionEngine()
        self.emotion = EmotionBasedEditor()
        self.music = MusicSyncEngine()
        self.beats = BeatAlignmentEngine()

    def finalize_timeline(
        self, 
        timeline: Dict[str, Any], 
        narrative_data: Dict[str, Any], 
        platform: str
    ) -> Dict[str, Any]:
        """
        Takes a raw timeline of generated scenes and applies adaptive 
        editing decisions (transitions, color grading, music sync).
        """
        logger.info("[AdaptiveEditor] Finalizing timeline based on narrative data.")
        
        # 1. Determine Strategy
        curve = narrative_data.get("emotional_graph", [])
        style = self.strategy.select_strategy(curve, platform)
        timeline["transition_style"] = style
        
        # 2. Apply Transitions
        timeline = self.transitions.apply_transitions(timeline, style)
        
        # 3. Emotion-based grading
        timeline = self.emotion.adjust_color_grading(timeline, curve)
        
        # 4. Music selection
        tension = narrative_data.get("metrics", {}).get("tension", 50.0)
        music_style = self.music.select_music_intensity(tension)
        timeline["music_style"] = music_style
        timeline["stage"] = platform
        
        # 5. Beat alignment (mock audio beats)
        mock_beats = [1.5, 3.0, 4.5]
        timeline = self.beats.align_cuts_to_beats(timeline, mock_beats)
        
        logger.info(f"[AdaptiveEditor] Timeline finalized using strategy '{style}'.")
        return timeline
