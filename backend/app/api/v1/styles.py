"""Styles API — /api/v1/styles/

Endpoints for querying viral style presets and their configurations.
Returns prompt modifiers, FFmpeg filters, caption styles, and pacing profiles.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.viral_intelligence import ViralStyle
from app.services.styles.viral_styles import ViralStyleConfig

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Styles"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class StyleConfigResponse(BaseModel):
    style_id: str
    name: str
    prompt_modifier: str
    camera_motion: str
    ffmpeg_filters: str
    transitions: str
    sound_profile: str
    captions_style: str


class StyleApplyRequest(BaseModel):
    style_id: str
    base_prompt: str


class StyleApplyResponse(BaseModel):
    style_id: str
    enhanced_prompt: str
    ffmpeg_filters: str
    captions_style: str
    camera_motion: str
    transitions: str
    sound_profile: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=List[StyleConfigResponse],
    summary="List all available viral styles",
    description=(
        "Returns all 7 viral content styles with their full configuration: "
        "prompt modifiers for SDXL, FFmpeg filter chains, caption styles, "
        "camera motion profiles, transitions, and sound profiles."
    ),
)
async def list_styles():
    """Return all viral style configurations."""
    config = ViralStyleConfig()
    all_styles = config.get_all_styles()
    return [
        StyleConfigResponse(
            style_id=s["style_id"],
            name=s["name"],
            prompt_modifier=s["prompt_modifier"],
            camera_motion=s["camera_motion"],
            ffmpeg_filters=s["ffmpeg_filters"],
            transitions=s["transitions"],
            sound_profile=s["sound_profile"],
            captions_style=s["captions_style"],
        )
        for s in all_styles
    ]


@router.get(
    "/{style_id}",
    response_model=StyleConfigResponse,
    summary="Get a specific viral style configuration",
    description="Returns the full configuration for a single style preset by its ID.",
)
async def get_style(style_id: str):
    """Return configuration for a specific style."""
    try:
        style_enum = ViralStyle(style_id.lower())
    except ValueError:
        valid = [s.value for s in ViralStyle]
        raise HTTPException(
            status_code=404,
            detail=f"Style '{style_id}' not found. Valid styles: {valid}",
        )

    config = ViralStyleConfig()
    style_config = config.get_style_config(style_enum)

    return StyleConfigResponse(
        style_id=style_id,
        name=style_config["name"],
        prompt_modifier=style_config["prompt_modifier"],
        camera_motion=style_config["camera_motion"],
        ffmpeg_filters=style_config["ffmpeg_filters"],
        transitions=style_config["transitions"],
        sound_profile=style_config["sound_profile"],
        captions_style=style_config["captions_style"],
    )


@router.post(
    "/apply",
    response_model=StyleApplyResponse,
    summary="Apply a style to a base prompt",
    description=(
        "Takes a base SDXL prompt and a style ID, and returns an enhanced prompt "
        "with all style modifiers applied, plus FFmpeg and caption configurations "
        "ready for the video generation pipeline."
    ),
)
async def apply_style(body: StyleApplyRequest):
    """Merge a base prompt with a viral style's modifiers."""
    try:
        style_enum = ViralStyle(body.style_id.lower())
    except ValueError:
        valid = [s.value for s in ViralStyle]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid style_id '{body.style_id}'. Valid: {valid}",
        )

    config = ViralStyleConfig()
    style_data = config.get_style_config(style_enum)

    # Compose enhanced prompt by appending style modifiers
    enhanced_prompt = f"{body.base_prompt.rstrip(', ')}, {style_data['prompt_modifier']}"

    logger.info(f"Applied style '{body.style_id}' to prompt.")

    return StyleApplyResponse(
        style_id=body.style_id,
        enhanced_prompt=enhanced_prompt,
        ffmpeg_filters=style_data["ffmpeg_filters"],
        captions_style=style_data["captions_style"],
        camera_motion=style_data["camera_motion"],
        transitions=style_data["transitions"],
        sound_profile=style_data["sound_profile"],
    )


@router.get(
    "/ids/list",
    summary="Get a simple list of all style IDs",
    response_model=List[str],
)
async def list_style_ids():
    """Return just the list of valid style_id strings."""
    return [s.value for s in ViralStyle]
