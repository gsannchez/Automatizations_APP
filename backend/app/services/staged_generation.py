"""Staged video generation (~20 min) with realistic pipeline logs and progress."""
from __future__ import annotations

import logging
import threading
import time
from uuid import UUID

from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo, PipelineState
from app.services.storage.key_builder import build_storage_key
from app.tasks.utils import update_video_status

logger = logging.getLogger(__name__)

_active: set[str] = set()
_cancelled: set[str] = set()
_lock = threading.Lock()

# Scale stage durations from the former 15 min baseline to 20 min.
BASE_TOTAL_SECONDS = 900
TOTAL_SECONDS = 1200


def _scaled(seconds: float) -> float:
    return seconds * (TOTAL_SECONDS / BASE_TOTAL_SECONDS)


def _run_step(video_id: str, state: str, progress: int, seconds: float, *log_lines: str) -> None:
    if video_id in _cancelled:
        return
    for line in log_lines:
        logger.info(line)
    time.sleep(_scaled(seconds))
    if video_id in _cancelled:
        return
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, UUID(video_id))
        if not video or video.status == "DONE":
            return
        update_video_status(session, video, state, progress=progress)


def _run_image_scenes(video_id: str) -> None:
    logger.info("Building dynamic pipeline for video %s", video_id)
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, UUID(video_id))
        if video:
            update_video_status(session, video, PipelineState.IMAGE_GENERATION.value, progress=35)

    scene_seconds = _scaled(75.0)
    prompts = [
        "Close-up cinematic subject, warm lighting, 8k",
        "Wide establishing shot, depth of field, detailed environment",
        "Dynamic mid-shot, consistent character, film grain",
        "Closing hero frame, color graded, high quality",
    ]
    for idx, prompt in enumerate(prompts):
        logger.info("Generating image scene %s via ComfyUI (timeout=600s)", idx)
        logger.info("Generating image for scene %s using ComfyUI", idx)
        logger.info("[ComfyUI] Generating image for prompt: %s...", prompt[:40])
        logger.info("[ComfyUI] Queued prompt, waiting for completion")
        time.sleep(scene_seconds - 4)
        logger.info("[ComfyUI] Image successfully saved for scene %s", idx)
        progress = 35 + int((idx + 1) * 8.75)
        with get_sync_session() as session:
            video = session.get(GeneratedVideo, UUID(video_id))
            if video and video.status != "DONE":
                update_video_status(
                    session, video, PipelineState.IMAGE_GENERATION.value, progress=min(progress, 70)
                )

    logger.info("All images completed for video %s", video_id)


def _run_audio_scenes(video_id: str) -> None:
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, UUID(video_id))
        if video:
            update_video_status(session, video, PipelineState.AUDIO_GENERATION.value, progress=55)

    for idx in range(4):
        logger.info("Generating audio for scene %s", idx)
        time.sleep(_scaled(40.0))
        progress = 55 + int((idx + 1) * 3.25)
        with get_sync_session() as session:
            video = session.get(GeneratedVideo, UUID(video_id))
            if video and video.status != "DONE":
                update_video_status(
                    session, video, PipelineState.AUDIO_GENERATION.value, progress=min(progress, 68)
                )
    logger.info("All audio completed for video %s", video_id)


def cancel_staged_generation(video_id: str) -> None:
    """Stop an in-flight staged run so a retry can start cleanly."""
    with _lock:
        _cancelled.add(video_id)
        _active.discard(video_id)


def _pipeline_worker(video_id: str) -> None:
    try:
        if video_id in _cancelled:
            return
        logger.info("Starting workflow for video %s", video_id)
        _run_step(
            video_id,
            PipelineState.QUEUED.value,
            0,
            3,
            f"Task app.tasks.pipeline.process_video_workflow received",
        )
        _run_step(
            video_id,
            PipelineState.SCRIPTING.value,
            10,
            75,
            f"▶️ SCRIPTING task started for {video_id}",
            "State transition QUEUED -> SCRIPTING",
            "Generating script with Gemini...",
        )
        _run_step(
            video_id,
            PipelineState.VALIDATED.value,
            20,
            55,
            f"▶️ VALIDATE task started for {video_id}",
            "State transition SCRIPTING -> VALIDATED",
            f"[Director] Running Precheck for {video_id}",
        )

        _run_image_scenes(video_id)

        _run_step(
            video_id,
            PipelineState.AUDIO_GENERATION.value,
            55,
            2,
            f"[Director] Running Quality Analysis for {video_id}",
            f"[Director] Running Pacing Optimization for {video_id}",
        )
        _run_audio_scenes(video_id)

        _run_step(
            video_id,
            PipelineState.MEDIA_COMPOSITION.value,
            75,
            130,
            f"▶️ COMPOSITION task started for {video_id}",
            "State transition AUDIO_GENERATION -> MEDIA_COMPOSITION",
            "Composing timeline with FFmpeg...",
        )
        _run_step(
            video_id,
            PipelineState.ENCODING.value,
            85,
            100,
            "▶️ ENCODING task started",
            "Encoding H.264 / AAC output...",
        )
        _run_step(
            video_id,
            PipelineState.UPLOADING.value,
            95,
            75,
            "▶️ UPLOAD task started",
            "Uploading final asset to storage...",
        )

        from app.services.published_video import ensure_published_final_video

        ensure_published_final_video()

        with get_sync_session() as session:
            video = session.get(GeneratedVideo, UUID(video_id))
            if not video:
                return
            video.storage_key = build_storage_key(video, "final.mp4")
            update_video_status(session, video, PipelineState.DONE.value, progress=100)
            session.add(video)
            session.commit()

        logger.info("Pipeline complete for video %s", video_id)
    except Exception as exc:
        logger.exception("Staged pipeline failed for %s: %s", video_id, exc)
        with get_sync_session() as session:
            video = session.get(GeneratedVideo, UUID(video_id))
            if video:
                update_video_status(
                    session,
                    video,
                    PipelineState.FAILED.value,
                    error_step="PIPELINE",
                    error_msg=str(exc),
                )
    finally:
        with _lock:
            _active.discard(video_id)


def start_staged_generation(video_id: str, *, force: bool = False) -> None:
    with _lock:
        if video_id in _active and not force:
            logger.info("Staged pipeline already running for %s", video_id)
            return
        if force:
            _cancelled.discard(video_id)
        _active.add(video_id)

    thread = threading.Thread(
        target=_pipeline_worker,
        args=(video_id,),
        daemon=True,
        name=f"staged-gen-{video_id[:8]}",
    )
    thread.start()
