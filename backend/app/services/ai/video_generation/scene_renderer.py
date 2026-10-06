"""Render one scene to a finished clip: motion + text overlay + TTS audio.

Strategy per scene:
  1. Ask ``VideoGeneratorFactory`` for the best IMAGE_TO_VIDEO backend
     (SVD first on 8-12 GB). If one is available, generate real motion from the
     scene's still image.
  2. If no adapter is available (or it fails), fall back to the ffmpeg Ken Burns
     pan/zoom over the still — the video still renders, just less dynamic.
  3. Either way the clip is muxed with the scene's TTS audio, normalised to
     1080x1920 @30fps, with the on-screen text overlaid.

The duration is driven by the *audio* (what the viewer hears), not by the model.
SVD produces ~3.5s clips, far shorter than a narration line, so the motion is
turned into a seamless ping-pong loop (forward + reverse, built once into a temp
file) and then repeated to fill the scene. The audio is padded with silence
rather than truncated, so a short line never cuts the scene short.
"""
from __future__ import annotations

import logging
import math
import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.services.monitoring.cuda_cleanup import CUDACleanup
from app.services.storage import storage
from app.services.video_generator import VideoGenerator
from app.services.video_generator_future import (
    GenerationMode,
    VideoGenerationRequest,
    VideoGeneratorFactory,
)
from app.utils.media_utils import get_audio_duration

logger = logging.getLogger(__name__)

WIDTH = settings.VIDEO_WIDTH
HEIGHT = settings.VIDEO_HEIGHT
FPS = settings.VIDEO_FPS

# Never render a scene shorter than this, even if the TTS clip is tiny.
MIN_SCENE_SECONDS = 2.5
# How long ffmpeg gets for a single scene (SVD + encode).
SCENE_RENDER_TIMEOUT = 900


# ---------------------------------------------------------------------------
# Motion backends
# ---------------------------------------------------------------------------

def try_generate_motion(image_key: str, scene: Dict[str, Any]) -> Optional[str]:
    """Generate a motion clip from *image_key*. Returns a local path, or None.

    Returning ``None`` is not an error — the caller falls back to Ken Burns.
    """
    if settings.VIDEO_BACKEND in ("ffmpeg", "none"):
        return None

    try:
        adapter = VideoGeneratorFactory().get_best_available(
            GenerationMode.IMAGE_TO_VIDEO
        )
    except Exception as exc:  # pragma: no cover - factory/env dependent
        logger.warning("Could not resolve a video backend: %s", exc)
        return None

    if adapter is None:
        logger.info("No IMAGE_TO_VIDEO backend available — using Ken Burns fallback")
        return None

    request = VideoGenerationRequest(
        prompt=scene.get("image_prompt") or scene.get("text") or "",
        mode=GenerationMode.IMAGE_TO_VIDEO,
        input_image_path=storage.get_local_path(image_key),
        seed=scene.get("seed"),
    )

    try:
        result = adapter.generate(request)
    except Exception as exc:  # pragma: no cover - GPU/env dependent
        logger.error("Motion backend %s raised: %s", adapter.backend_id.value, exc)
        return None
    finally:
        CUDACleanup.force_cleanup()

    if not result.success or not result.output_path:
        logger.warning(
            "Motion backend %s failed (%s) — falling back to Ken Burns",
            adapter.backend_id.value,
            result.error,
        )
        return None

    logger.info(
        "Scene motion generated with %s in %.1fs (%s frames)",
        result.backend_used,
        result.generation_time_seconds,
        result.metadata.get("num_frames"),
    )
    return result.output_path


# ---------------------------------------------------------------------------
# ffmpeg builders
# ---------------------------------------------------------------------------

def _make_pingpong(clip_path: str, out_path: str) -> None:
    """Write ``clip + reverse(clip)`` to *out_path*.

    The result starts and ends on the clip's first frame, so repeating it is
    seamless. ``reverse`` buffers the whole stream, which is cheap here because
    the input is a single ~3.5s SVD clip rather than the already-looped video.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", clip_path,
        "-filter_complex",
        "[0:v]split=2[f][b];[b]reverse[r];[f][r]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-an",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "veryfast", "-crf", "18",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=SCENE_RENDER_TIMEOUT)


def _motion_filter() -> str:
    """Fit the (already ping-ponged) motion to the canvas, then overlay text."""
    return (
        f"[0:v]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,fps={FPS}[v0];"
        "[v0][1:v]overlay=0:0[v]"
    )


def _kenburns_filter(duration: float, zoom_in: bool) -> str:
    frames = max(int(duration * FPS), FPS)
    if zoom_in:
        zoom = "zoompan=z='min(zoom+0.0015,1.5)'"
    else:
        zoom = "zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))'"
    return (
        f"[0:v]{zoom}:d={frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}:fps={FPS}[bg];"
        "[bg]setsar=1[v0];"
        "[v0][1:v]overlay=0:0[v]"
    )


def _build_command(
    motion_path: Optional[str],
    image_path: str,
    overlay_path: str,
    audio_path: Optional[str],
    duration: float,
    clip_seconds: float,
    zoom_in: bool,
    output_path: str,
) -> List[str]:
    """Assemble the ffmpeg argv for one scene clip.

    Input 0 is always the visual (motion clip or still), input 1 the text
    overlay and input 2 the audio — synthesised silence when a scene has no
    narration, so the filter graph and stream mapping stay uniform.

    The audio is padded with ``apad`` and the length is pinned by ``-t``: using
    ``-shortest`` instead would truncate the scene to a short narration line.
    """
    if audio_path:
        audio_inputs = ["-i", audio_path]
    else:
        audio_inputs = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]

    if motion_path:
        # The input is already seamless; repeat it enough times to cover the
        # scene. ``-stream_loop N`` plays the file N+1 times, and ``-t`` trims
        # the overshoot.
        loops = max(int(math.ceil(duration / max(clip_seconds, 0.1))), 1)
        inputs = ["-stream_loop", str(loops), "-i", motion_path, "-i", overlay_path]
        graph = _motion_filter()
    else:
        inputs = ["-loop", "1", "-i", image_path, "-i", overlay_path]
        graph = _kenburns_filter(duration, zoom_in=zoom_in)

    return [
        "ffmpeg", "-y",
        *inputs,
        *audio_inputs,
        "-filter_complex", f"{graph};[2:a]apad[a]",
        "-map", "[v]", "-map", "[a]",
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        output_path,
    ]


def _probe_clip_seconds(path: str) -> float:
    """Duration of a clip, used to size the repeat count."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
        return float(out.stdout.strip())
    except Exception as exc:
        logger.debug("Could not probe clip duration (%s); assuming 3.5s", exc)
        return 3.5


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def render_scene_clip(video, scene: Dict[str, Any], scene_idx: int, out_key: str) -> str:
    """Render scene *scene_idx* and save the clip to *out_key* in storage.

    Raises:
        ValueError: if the scene has no image (the image stage must run first).
        RuntimeError: if ffmpeg fails or times out.
    """
    image_key = scene.get("image_path")
    if not image_key:
        raise ValueError(f"Scene {scene_idx} has no image_path; run image generation first")

    audio_key = scene.get("audio_path")
    if audio_key:
        duration = max(get_audio_duration(audio_key), MIN_SCENE_SECONDS)
    else:
        duration = 4.0
        logger.warning(
            "Scene %s has no audio_path — rendering a silent %.1fs clip",
            scene_idx,
            duration,
        )

    text = scene.get("on_screen_text") or scene.get("text") or ""

    local_image = storage.get_local_path(image_key)

    overlay_key = out_key.replace(".mp4", "_overlay.png")
    VideoGenerator()._create_text_overlay(text, overlay_key)
    local_overlay = storage.get_local_path(overlay_key)

    motion_path = try_generate_motion(image_key, scene)
    pingpong_path: Optional[str] = None
    clip_seconds = 0.0
    if motion_path:
        fd, pingpong_path = tempfile.mkstemp(
            suffix=".mp4", prefix=f"sceneloop_{scene_idx}_"
        )
        os.close(fd)
        _make_pingpong(motion_path, pingpong_path)
        clip_seconds = _probe_clip_seconds(pingpong_path)

    fd, local_out = tempfile.mkstemp(suffix=".mp4", prefix=f"scene_{scene_idx}_")
    os.close(fd)

    cmd = _build_command(
        motion_path=pingpong_path,
        image_path=local_image,
        overlay_path=local_overlay,
        audio_path=storage.get_local_path(audio_key) if audio_key else None,
        duration=duration,
        clip_seconds=clip_seconds,
        # Alternate the fallback pan direction so consecutive scenes differ.
        zoom_in=scene_idx % 2 == 0,
        output_path=local_out,
    )

    try:
        logger.info(
            "Rendering scene %s (%.1fs, %s)",
            scene_idx,
            duration,
            "SVD motion" if pingpong_path else "Ken Burns",
        )
        subprocess.run(cmd, check=True, capture_output=True, timeout=SCENE_RENDER_TIMEOUT)
        with open(local_out, "rb") as fh:
            storage.save(fh, out_key)
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or b"").decode("utf-8", "replace")[-800:]
        raise RuntimeError(f"ffmpeg failed for scene {scene_idx}: {stderr}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"ffmpeg timed out after {SCENE_RENDER_TIMEOUT}s for scene {scene_idx}"
        ) from exc
    finally:
        for path in (local_out, motion_path, pingpong_path):
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        CUDACleanup.force_cleanup()

    return out_key
