from ..visual_fx.camera_motion import CameraMotionEngine
from ..visual_fx.cinematic_filters import CinematicFilters
from ..hooks.attention_grabber import AttentionGrabber

class SceneComposer:
    """
    Composes the visual filter graph for a single scene image.
    Combines camera motion, cinematic filters, and potential hook effects.
    """
    
    @staticmethod
    def get_scene_filter(scene_idx: int, duration: float, width: int = 1080, height: int = 1920, style: str = "tiktok", sub_index: int = 0) -> str:
        """
        Returns the video filter string for a scene.
        """
        filters = []
        
        # 1. Scale and crop to fit vertical
        filters.append(f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}")
        
        # 2. Camera Motion
        # If it's the very first scene, we might want an aggressive hook zoom
        if scene_idx == 0 and sub_index == 0:
            motion = AttentionGrabber.get_hook_visual_filter()
        else:
            motion = CameraMotionEngine.get_motion_filter(duration, width, height, style, sub_index)
            
        filters.append(motion)
        
        # 3. Cinematic Filters (Color grading, grain, etc.)
        style_filter = CinematicFilters.get_filter_string(style)
        if style_filter:
            filters.append(style_filter)
            
        # 4. Setsar to ensure pixels are square
        filters.append("setsar=1")
        
        return ",".join(filters)
