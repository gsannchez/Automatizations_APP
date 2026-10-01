import logging
from uuid import UUID

from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.video_generator import VideoGenerator
from ..services.video_job_service import VideoJobService
from ..services.storage.key_builder import build_storage_key
from .utils import update_video_status
from .task_helpers import raise_or_retry

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.composition.compose_video_task", bind=True, max_retries=3)
def compose_video_task(self, video_id_str: str):
    logger.info(f"▶️ COMPOSITION task started for {video_id_str}")
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
                raise ValueError("No se encontraron escenas en la base de datos para la composición.")
                
            canonical_key = build_storage_key(video, "final.mp4")
            inner_path = canonical_key.replace("videos/", "", 1)
            final_path = VideoGenerator().assemble_video(scenes, output_filename=inner_path)
            
            if not final_path:
                raise RuntimeError("Video assembly returned no output path")

            video.storage_key = final_path
            session.add(video)
            session.commit()
            job_service.mark_success(job.id)
            logger.info("Video assembled: %s", final_path)
            return video_id_str

        except Exception as exc:
            job_service.mark_failure(job.id, str(exc))
            update_video_status(
                session,
                video,
                PipelineState.FAILED.value,
                error_step="MEDIA_COMPOSITION",
                error_msg=str(exc),
            )
            raise_or_retry(self, exc, countdown=30)
