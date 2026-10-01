import logging
from uuid import UUID
from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.video_job_service import VideoJobService
from .utils import update_video_status

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.upload.upload_task", bind=True)
def upload_task(self, video_id_str: str):
    logger.info(f"▶️ UPLOAD task started for {video_id_str}")
    video_id = UUID(video_id_str)
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str
            
        job_service = VideoJobService(session)
        upload_job = job_service.create_job(video_id, PipelineState.UPLOADING.value)
        update_video_status(session, video, PipelineState.UPLOADING.value, progress=95)
        # Placeholder para la lógica de subida a YouTube/TikTok
        job_service.mark_success(upload_job.id)

        # Marcar como completado al final
        final_job = job_service.create_job(video_id, PipelineState.DONE.value)
        update_video_status(session, video, PipelineState.DONE.value, progress=100)
        job_service.mark_success(final_job.id)
        logger.info(f"🎉 Workflow fully completed for Video ID: {video_id_str}")
        return video_id_str
