"""Phase 8: Platform Strategy Engine — per-platform render/caption/pacing profiles."""
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class PlatformPresetName(str, Enum):
    TIKTOK_AGGRESSIVE = "TIKTOK_AGGRESSIVE"
    REELS_CLEAN = "REELS_CLEAN"
    SHORTS_STORYTELLING = "SHORTS_STORYTELLING"


@dataclass
class PlatformProfile:
    name: str
    pacing_multiplier: float
    subtitle_size: int
    hook_speed: str
    scene_duration_max: float
    cta_style: str
    zoom_intensity: float
    caption_placement: str
    transition_style: str
    max_duration_secs: float


PLATFORM_PROFILES: Dict[str, PlatformProfile] = {
    "TIKTOK": PlatformProfile(
        name="TikTok",
        pacing_multiplier=1.3,
        subtitle_size=52,
        hook_speed="ultra_fast",
        scene_duration_max=3.5,
        cta_style="aggressive",
        zoom_intensity=1.6,
        caption_placement="center",
        transition_style="snap_cut",
        max_duration_secs=60.0,
    ),
    "INSTAGRAM_REELS": PlatformProfile(
        name="Instagram Reels",
        pacing_multiplier=1.0,
        subtitle_size=44,
        hook_speed="medium",
        scene_duration_max=5.0,
        cta_style="clean",
        zoom_intensity=1.1,
        caption_placement="bottom_third",
        transition_style="smooth_fade",
        max_duration_secs=90.0,
    ),
    "YOUTUBE_SHORTS": PlatformProfile(
        name="YouTube Shorts",
        pacing_multiplier=1.1,
        subtitle_size=56,
        hook_speed="fast",
        scene_duration_max=6.0,
        cta_style="storytelling",
        zoom_intensity=1.2,
        caption_placement="center",
        transition_style="cross_dissolve",
        max_duration_secs=60.0,
    ),
}


class PlatformStrategyEngine:
    """Returns the canonical platform profile for a given platform string."""

    @staticmethod
    def get_profile(platform: str) -> PlatformProfile:
        key = platform.upper().replace(" ", "_")
        return PLATFORM_PROFILES.get(key, PLATFORM_PROFILES["TIKTOK"])

    @staticmethod
    def to_dict(profile: PlatformProfile) -> dict:
        return {
            "name": profile.name,
            "pacing_multiplier": profile.pacing_multiplier,
            "subtitle_size": profile.subtitle_size,
            "hook_speed": profile.hook_speed,
            "scene_duration_max": profile.scene_duration_max,
            "cta_style": profile.cta_style,
            "zoom_intensity": profile.zoom_intensity,
            "caption_placement": profile.caption_placement,
            "transition_style": profile.transition_style,
            "max_duration_secs": profile.max_duration_secs,
        }
