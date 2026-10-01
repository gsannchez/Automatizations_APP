import logging
import os
from uuid import UUID

from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.comfyui_health import get_comfyui_status, is_comfyui_available
from ..services.video_job_service import VideoJobService
from .gpu_lock import acquire_gpu_lock, GPULockError
from .utils import update_video_status
from .task_helpers import raise_or_retry

logger = logging.getLogger(__name__)

GPU_LOCK_WAIT = int(os.getenv("GPU_LOCK_WAIT_SECONDS", "30"))
from ..core.config import settings as app_settings

COMFYUI_SCENE_TIMEOUT = app_settings.COMFYUI_SCENE_TIMEOUT_SECONDS


@celery_app.task(name="app.tasks.image_generation.generate_image_task", bind=True, max_retries=2)
def generate_image_task(self, video_id_str: str, scene_idx: int):
    video_id = UUID(video_id_str)

    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str

        update_video_status(session, video, PipelineState.IMAGE_GENERATION.value, progress=35)

        scenes = video.scenes_data
        scene_prog = video.scene_progress or {}
        idx = str(scene_idx)

        if scene_prog.get(idx, {}).get("image") == "done":
            logger.info("Scene %s image already done, skipping", scene_idx)
            return video_id_str

        job_service = VideoJobService(session)
        job = job_service.create_job(video_id, PipelineState.IMAGE_GENERATION.value)

        try:
            from ..services.image_generator import generate_images_for_scenes
            from ..services.storage import storage

            if not is_comfyui_available():
                status = get_comfyui_status()
                raise RuntimeError(
                    f"ComfyUI no disponible ({status['url']}). "
                    "Abre ComfyUI en el puerto 8188 o revisa COMFYUI_URL en .env"
                )

            scene = scenes[scene_idx]
            with acquire_gpu_lock(timeout=600, blocking_timeout=GPU_LOCK_WAIT):
                logger.info("Generating image scene %s via ComfyUI (timeout=%ss)", scene_idx, COMFYUI_SCENE_TIMEOUT)
                paths = generate_images_for_scenes(
                    [scene],
                    timeout_seconds=COMFYUI_SCENE_TIMEOUT,
                )
                scene_path = paths[0]

            if not scene_path or "fallback_" in scene_path:
                raise RuntimeError(
                    f"ComfyUI no generó imagen válida para escena {scene_idx}"
                )

            scene["image_path"] = scene_path
            scene_prog.setdefault(idx, {})["image"] = "done"

            video.scenes_data = scenes
            video.scene_progress = scene_prog
            session.add(video)
            session.commit()
            job_service.mark_success(job.id)
            logger.info("Image done for scene %s: %s", scene_idx, scene_path)
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
