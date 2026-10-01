import logging
from uuid import UUID
from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.video_job_service import VideoJobService
from .utils import update_video_status

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.encoding.encode_video_task", bind=True)
def encode_video_task(self, video_id_str: str):
    logger.info(f"▶️ ENCODING task started for {video_id_str}")
    video_id = UUID(video_id_str)
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str
            
        job_service = VideoJobService(session)
        job = job_service.create_job(video_id, PipelineState.ENCODING.value)
        update_video_status(session, video, PipelineState.ENCODING.value, progress=85)
        # Placeholder para encoding futuro (HLS, resoluciones, etc)
        job_service.mark_success(job.id)
        return video_id_str
