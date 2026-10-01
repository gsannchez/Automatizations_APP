import logging
from uuid import UUID

from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState

from .scripting import scripting_task, validate_task
from .image_generation import generate_image_task, images_complete_callback
from .audio_generation import generate_audio_task, audio_complete_callback
from .composition import compose_video_task
from .encoding import encode_video_task
from .upload import upload_task
from .director_tasks import (
    director_precheck_task,
    director_quality_analysis_task,
    director_pacing_optimization_task,
    director_final_analysis_task,
)
from .utils import update_video_status

logger = logging.getLogger(__name__)


def _fail_video(video_id_str: str, step: str, message: str) -> None:
    video_id = UUID(video_id_str)
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if video:
            update_video_status(
                session,
                video,
                PipelineState.FAILED.value,
                error_step=step,
                error_msg=message,
            )


@celery_app.task(name="app.tasks.pipeline.build_dynamic_pipeline", bind=True)
def build_dynamic_pipeline(self, video_id_str: str):
    logger.info("Building dynamic pipeline for video %s", video_id_str)

    with get_sync_session() as session:
        video = session.get(GeneratedVideo, UUID(video_id_str))
        if not video or not video.scenes_data:
            raise ValueError("No scenes found for pipeline build")
        scene_count = len(video.scenes_data)

    for i in range(scene_count):
        generate_image_task.run(video_id_str, i)

    images_complete_callback.run(video_id_str)

    for i in range(scene_count):
        generate_audio_task.run(video_id_str, i)

    audio_complete_callback.run(video_id_str)

    director_quality_analysis_task.run(video_id_str)
    director_pacing_optimization_task.run(video_id_str)
    compose_video_task.run(video_id_str)

    with get_sync_session() as session:
        video = session.get(GeneratedVideo, UUID(video_id_str))
        if not video or not video.storage_key:
            raise RuntimeError("Composition did not produce a final video file")

    director_final_analysis_task.run(video_id_str)
    encode_video_task.run(video_id_str)
    upload_task.run(video_id_str)

    return video_id_str


@celery_app.task(name="app.tasks.pipeline.process_video_workflow", bind=True)
def process_video_workflow(self, video_id_str: str):
    logger.info("Starting workflow for video %s", video_id_str)

    try:
        scripting_task.run(video_id_str)
        validate_task.run(video_id_str)
        director_precheck_task.run(video_id_str)
        build_dynamic_pipeline.run(video_id_str)
    except Exception as e:
        logger.error("Pipeline failed for %s: %s", video_id_str, e, exc_info=True)
        _fail_video(video_id_str, "PIPELINE", str(e))
        raise

    return video_id_str
