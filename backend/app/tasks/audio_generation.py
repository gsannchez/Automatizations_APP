import logging
from uuid import UUID

from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.storage.key_builder import build_storage_key
from ..services.tts.provider import synthesize
from ..services.video_job_service import VideoJobService
from ..utils.media_utils import get_audio_duration
from .task_helpers import raise_or_retry
from .utils import update_video_status

logger = logging.getLogger(__name__)


def _narration_text(scene: dict, scene_idx: int) -> str:
    return (
        scene.get("voiceover_text")
        or scene.get("text")
        or scene.get("narration")
        or ""
    ).strip() or f"Scene {scene_idx + 1}"


@celery_app.task(name="app.tasks.audio_generation.generate_audio_task", bind=True, max_retries=3)
def generate_audio_task(self, video_id_str: str, scene_idx: int):
    video_id = UUID(video_id_str)

    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str

        update_video_status(session, video, PipelineState.AUDIO_GENERATION.value, progress=55)

        scenes = video.scenes_data
        if not scenes or scene_idx >= len(scenes):
            logger.warning("Scene %s out of range for video %s", scene_idx, video_id)
            return video_id_str

        scene_prog = video.scene_progress or {}
        idx = str(scene_idx)

        if scene_prog.get(idx, {}).get("audio") == "done":
            logger.info("Scene %s audio already generated, skipping", scene_idx)
            return video_id_str

        job_service = VideoJobService(session)
        job = job_service.create_job(video_id, PipelineState.AUDIO_GENERATION.value)

        try:
            scene = scenes[scene_idx]
            text = _narration_text(scene, scene_idx)

            audio_key = build_storage_key(video, f"audio/{scene_idx}.mp3")
            logger.info("Synthesising audio for scene %s with %s", scene_idx, "configured provider")
            synthesize(text, audio_key, language=scene.get("language"))

            duration = get_audio_duration(audio_key)

            scene["audio_path"] = audio_key
            scene["duration"] = duration
            scene["status"] = "AUDIO_GENERATED"
            scene_prog.setdefault(idx, {})["audio"] = "done"

            video.scenes_data = scenes
            video.scene_progress = scene_prog
            session.add(video)
            session.commit()
            job_service.mark_success(job.id)

            logger.info("Audio done for scene %s: %s (%.1fs)", scene_idx, audio_key, duration)
            return video_id_str

        except Exception as exc:
            job_service.mark_failure(job.id, str(exc))
            logger.error("Audio scene %s failed: %s", scene_idx, exc, exc_info=True)
            raise_or_retry(self, exc, countdown=15)


@celery_app.task(name="app.tasks.audio_generation.audio_complete_callback", bind=True)
def audio_complete_callback(self, video_id_str: str, results=None):
    logger.info("All audio completed for video %s", video_id_str)
    return video_id_str
