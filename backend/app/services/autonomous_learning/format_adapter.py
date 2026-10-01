from enum import Enum
from dataclasses import dataclass

class PlatformType(str, Enum):
    TIKTOK = "TIKTOK"
    YOUTUBE_SHORTS = "YOUTUBE_SHORTS"
    INSTAGRAM_REELS = "INSTAGRAM_REELS"

@dataclass
class FormatPreset:
    pacing_multiplier: float
    subtitle_size: int
    hook_speed: str
    scene_duration_max: float
    cta_style: str
    zoom_intensity: float
    caption_placement: str

class FormatAdapter:
    """Adapts content automatically based on platform."""
    
    PRESETS = {
        PlatformType.TIKTOK: FormatPreset(
            pacing_multiplier=1.2,
            subtitle_size=48,
            hook_speed="fast",
            scene_duration_max=4.0,
            cta_style="aggressive",
            zoom_intensity=1.5,
            caption_placement="center"
        ),
        PlatformType.INSTAGRAM_REELS: FormatPreset(
            pacing_multiplier=1.0,
            subtitle_size=42,
            hook_speed="medium",
            scene_duration_max=5.0,
            cta_style="clean",
            zoom_intensity=1.1,
            caption_placement="bottom"
        ),
        PlatformType.YOUTUBE_SHORTS: FormatPreset(
            pacing_multiplier=1.1,
            subtitle_size=54,
            hook_speed="fast",
            scene_duration_max=6.0,
            cta_style="storytelling",
            zoom_intensity=1.2,
            caption_placement="center"
        )
    }

    @classmethod
    def get_preset(cls, platform: str) -> FormatPreset:
        try:
            p = PlatformType(platform.upper())
            return cls.PRESETS[p]
        except ValueError:
            return cls.PRESETS[PlatformType.TIKTOK]
