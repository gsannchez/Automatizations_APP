"""
app/services/timeline/scene_timeline_engine.py

Responsible for defining and merging the canonical scene structure.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class SceneTimelineEngine:
    @staticmethod
    def build_canonical_scene(scene_id: int, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Builds a fresh, standard scene structure from a script input."""
        return {
            "scene_id": scene_id,
            "text": script_data.get("text", ""),
            "emotion": script_data.get("emotion", "neutral"),
            "character": script_data.get("character", "narrator"),
            "image_path": None,
            "audio_path": None,
            "duration": 0.0,
            "status": "PENDING"
        }

    @staticmethod
    def merge_media_state(scene: Dict[str, Any], audio_path: str = None, duration: float = None, image_path: str = None) -> Dict[str, Any]:
        """Updates the scene state idempotently with new media paths and status."""
        if audio_path:
            scene["audio_path"] = audio_path
            if duration is not None:
                scene["duration"] = duration
            if scene["status"] == "PENDING":
                scene["status"] = "AUDIO_GENERATED"
                
        if image_path:
            scene["image_path"] = image_path
            
        if scene.get("audio_path") and scene.get("image_path"):
            scene["status"] = "READY"
            
        return scene

    @staticmethod
    def validate_timeline(scenes: List[Dict[str, Any]]) -> bool:
        """Ensures all scenes in the timeline are fully ready for render."""
        for scene in scenes:
            if scene.get("status") != "READY" or not scene.get("duration") or scene.get("duration") <= 0:
                logger.error(f"Timeline validation failed on scene {scene.get('scene_id')}. State: {scene}")
                return False
        return True
