"""
app/services/orchestration/scene_orchestrator.py

Orchestrates the lifecycle of scenes, managing states and triggering steps.
"""
import logging
from typing import List, Dict, Any
from app.services.timeline.scene_timeline_engine import SceneTimelineEngine

logger = logging.getLogger(__name__)

class SceneOrchestrator:
    def __init__(self):
        self.engine = SceneTimelineEngine()

    def initialize_scenes(self, script_scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Converts raw script outputs to canonical scenes."""
        logger.info(f"Initializing {len(script_scenes)} canonical scenes.")
        return [self.engine.build_canonical_scene(idx, s) for idx, s in enumerate(script_scenes)]

    def get_pending_audio_scenes(self, scenes: List[Dict[str, Any]]) -> List[int]:
        """Returns indexes of scenes needing audio generation."""
        return [idx for idx, s in enumerate(scenes) if not s.get("audio_path")]

    def get_pending_image_scenes(self, scenes: List[Dict[str, Any]]) -> List[int]:
        """Returns indexes of scenes needing image generation. Note: Requires audio duration first."""
        return [idx for idx, s in enumerate(scenes) if not s.get("image_path") and s.get("duration", 0) > 0]

    def update_scene_state(self, scenes: List[Dict[str, Any]], scene_idx: int, audio_path: str = None, duration: float = None, image_path: str = None) -> List[Dict[str, Any]]:
        """Updates and returns the scene list idempotently."""
        if 0 <= scene_idx < len(scenes):
            scenes[scene_idx] = self.engine.merge_media_state(scenes[scene_idx], audio_path, duration, image_path)
        return scenes
        
    def is_timeline_ready(self, scenes: List[Dict[str, Any]]) -> bool:
        """Checks if the entire sequence is ready for video rendering."""
        return self.engine.validate_timeline(scenes)
