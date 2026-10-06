import logging
import os
from uuid import UUID

from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.ai.video_generation.scene_renderer import render_scene_clip
from ..services.ai.video_generation.timeline import assemble_timeline
from ..services.storage import storage
from ..services.storage.key_builder import build_storage_key
from ..services.video_job_service import VideoJobService
from .task_helpers import raise_or_retry
from .utils import update_video_status

logger = logging.getLogger(__name__)


def _clip_exists(key: str) -> bool:
    try:
        return os.path.exists(storage.get_local_path(key))
    except Exception:
        return False


@celery_app.task(name="app.tasks.composition.compose_video_task", bind=True, max_retries=3)
def compose_video_task(self, video_id_str: str):
    logger.info("▶️ COMPOSITION task started for %s", video_id_str)
    video_id = UUID(video_id_str)

    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str

        update_video_status(session, video, PipelineState.MEDIA_COMPOSITION.value, progress=75)

        job_service = VideoJobService(session)
        job = job_service.create_job(video_id, PipelineState.MEDIA_COMPOSITION.value)

        try:
            scenes = video.scenes_data
            if not scenes:
                raise ValueError("No scenes found in the database for composition.")

            scene_prog = video.scene_progress or {}
            clip_keys = []

            # 1. Render (or reuse) one clip per scene. Scenes are rendered
            #    sequentially because the GPU backend can only hold one model
            #    at a time on 8-12 GB.
            for i, scene in enumerate(scenes):
                idx = str(i)
                clip_key = build_storage_key(video, f"clips/{i}.mp4")

                if scene_prog.get(idx, {}).get("video") == "done" and _clip_exists(clip_key):
                    logger.info("Scene %s clip already rendered, reusing", i)
                    clip_keys.append(clip_key)
                    continue

                render_scene_clip(video, scene, i, clip_key)

                scene["video_path"] = clip_key
                scene_prog.setdefault(idx, {})["video"] = "done"
                video.scenes_data = scenes
                video.scene_progress = scene_prog
                session.add(video)
                session.commit()
                clip_keys.append(clip_key)

            # 2. Join the clips with crossfades, music bed and loudness normalisation.
            final_key = build_storage_key(video, "final.mp4")
            assemble_timeline(clip_keys, final_key)

            video.storage_key = final_key
            session.add(video)
            session.commit()
            job_service.mark_success(job.id)
            logger.info("Video assembled: %s", final_key)
            return video_id_str

        except Exception as exc:
            job_service.mark_failure(job.id, str(exc))
            logger.error("Composition failed for %s: %s", video_id, exc, exc_info=True)
            update_video_status(
                session,
                video,
                PipelineState.FAILED.value,
                error_step="MEDIA_COMPOSITION",
                error_msg=str(exc),
            )
            raise_or_retry(self, exc, countdown=30)
