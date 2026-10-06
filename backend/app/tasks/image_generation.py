import asyncio
import hashlib
import logging
from uuid import UUID

from PIL import Image

from ..core.celery_app import celery_app
from ..core.config import settings as app_settings
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.comfyui_health import get_comfyui_status, is_comfyui_available
from ..services.storage import storage
from ..services.storage.key_builder import build_storage_key
from ..services.video_job_service import VideoJobService
from .gpu_lock import acquire_gpu_lock
from .utils import update_video_status
from .task_helpers import raise_or_retry

logger = logging.getLogger(__name__)

GPU_LOCK_WAIT = 30  # seconds to wait for the global GPU lock
COMFYUI_SCENE_TIMEOUT = app_settings.COMFYUI_SCENE_TIMEOUT_SECONDS

# 9:16 portrait. 768x1344 is an SDXL-friendly bucket whose aspect ratio (0.571)
# closely matches the 1080x1920 canvas (0.5625), so the later scale/crop fills
# the frame with almost no loss. The old 896x1152 (0.778) threw away ~28% of the
# image width to the centre crop.
SCENE_WIDTH = 768
SCENE_HEIGHT = 1344


def _stable_seed(*parts: object) -> int:
    """Deterministic seed so the same prompt/styles reuse the same image."""
    digest = hashlib.md5("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def _scene_prompt(scene: dict) -> str:
    return scene.get("image_prompt") or scene.get("text") or "cinematic scene, highly detailed"


def _generate_image_local_path(scene: dict) -> str:
    """Generate one image and return the *local* filesystem path.

    Tries ComfyUI first (primary backend), then the local diffusers SDXL
    pipeline, and finally a black placeholder so a single scene can never
    abort the whole video.
    """
    prompt = _scene_prompt(scene)
    negative = scene.get("negative_prompt") or ""
    style = scene.get("visual_style") or "cinematic"
    seed = scene.get("seed")
    if seed is None:
        seed = _stable_seed(prompt, style)

    if is_comfyui_available():
        try:
            from ..services.ai.image_generation.comfyui_generator import ComfyUIGenerator

            generator = ComfyUIGenerator()
            return asyncio.run(
                generator.generate_image(
                    prompt=prompt,
                    negative_prompt=negative,
                    width=SCENE_WIDTH,
                    height=SCENE_HEIGHT,
                    style=style,
                    seed=seed,
                    max_wait_seconds=COMFYUI_SCENE_TIMEOUT,
                )
            )
        except Exception as exc:
            status = get_comfyui_status()
            logger.warning("ComfyUI failed (%s) for scene, falling back to local SDXL", exc)
            _ = status  # keep for context in logs if needed

    # Fallback 1: local diffusers SDXL (no external server needed)
    try:
        from ..services.ai.image_generation.sdxl_generator import SDXLGenerator

        generator = SDXLGenerator()
        return asyncio.run(
            generator.generate_image(
                prompt=prompt,
                negative_prompt=negative,
                width=SCENE_WIDTH,
                height=SCENE_HEIGHT,
                style=style,
                seed=seed,
            )
        )
    except Exception as exc:
        logger.error("Local SDXL fallback failed: %s", exc, exc_info=True)

    # Fallback 2: black placeholder (loudly logged — never silent)
    logger.error("All image backends failed for prompt %r — using black placeholder", prompt)
    return _write_black_placeholder()


def _write_black_placeholder() -> str:
    import os
    import tempfile

    img = Image.new("RGB", (SCENE_WIDTH, SCENE_HEIGHT), color=(0, 0, 0))
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    img.save(path)
    return path


@celery_app.task(name="app.tasks.image_generation.generate_image_task", bind=True, max_retries=2)
def generate_image_task(self, video_id_str: str, scene_idx: int):
    video_id = UUID(video_id_str)

    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str

        update_video_status(session, video, PipelineState.IMAGE_GENERATION.value, progress=35)

        scenes = video.scenes_data
        if not scenes or scene_idx >= len(scenes):
            logger.warning("Scene %s out of range for video %s", scene_idx, video_id)
            return video_id_str

        scene_prog = video.scene_progress or {}
        idx = str(scene_idx)

        if scene_prog.get(idx, {}).get("image") == "done":
            logger.info("Scene %s image already done, skipping", scene_idx)
            return video_id_str

        job_service = VideoJobService(session)
        job = job_service.create_job(video_id, PipelineState.IMAGE_GENERATION.value)

        try:
            scene = scenes[scene_idx]

            with acquire_gpu_lock(timeout=COMFYUI_SCENE_TIMEOUT + 60, blocking_timeout=GPU_LOCK_WAIT):
                logger.info(
                    "Generating image scene %s (ComfyUI=%s, timeout=%ss)",
                    scene_idx,
                    is_comfyui_available(),
                    COMFYUI_SCENE_TIMEOUT,
                )
                local_path = _generate_image_local_path(scene)

            # Persist to storage under a deterministic per-scene key.
            storage_key = build_storage_key(video, f"images/{scene_idx}.png")
            with open(local_path, "rb") as fh:
                storage.save(fh, storage_key)

            scene["image_path"] = storage_key
            scene_prog.setdefault(idx, {})["image"] = "done"

            video.scenes_data = scenes
            video.scene_progress = scene_prog
            session.add(video)
            session.commit()
            job_service.mark_success(job.id)
            logger.info("Image done for scene %s: %s", scene_idx, storage_key)
            return video_id_str

        except Exception as exc:
            job_service.mark_failure(job.id, str(exc))
            logger.error("Image scene %s failed: %s", scene_idx, exc, exc_info=True)
            update_video_status(
                session,
                video,
                PipelineState.FAILED.value,
                error_step="IMAGE_GENERATION",
                error_msg=str(exc),
            )
            raise_or_retry(self, exc, countdown=30)


@celery_app.task(name="app.tasks.image_generation.images_complete_callback", bind=True)
def images_complete_callback(self, video_id_str: str, results=None):
    logger.info("All images completed for video %s", video_id_str)
    return video_id_str
