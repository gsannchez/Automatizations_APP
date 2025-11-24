from .core.celery_app import celery_app
from .services.video_generator import generate_and_store_video
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def generate_video_task(self, video_id: int):
    """
    Tarea de Celery para generar un video en segundo plano.
    """
    try:
        logger.info(f"🚀 Starting background video generation for ID: {video_id}")
        generate_and_store_video(video_id)
        logger.info(f"✅ Video generation completed for ID: {video_id}")
        return f"Video {video_id} generated successfully."
    except Exception as e:
        logger.error(f"❌ Error in video generation task: {e}")
        # Reintentar con backoff exponencial
        raise self.retry(exc=e, countdown=60)
