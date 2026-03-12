import logging
import traceback
from uuid import UUID

from .core.celery_app import celery_app
from .core.database import get_sync_session
from .models.generated_video import GeneratedVideo
from .services.video_job_service import VideoJobService
from .services.storage.key_builder import build_storage_key

logger = logging.getLogger(__name__)

# Frozen pipeline order
PIPELINE_STEPS = [
    "SCRIPTING",
    "SCRIPT_VALIDATED",
    "IMAGE_GENERATION",
    "VOICE_SYNTHESIS",
    "MEDIA_COMPOSITION",
    "ENCODING",
    "UPLOADING",
    "DONE"
]

@celery_app.task(bind=True, max_retries=3)
def process_video_workflow(self, video_id_str: str):
    """Orchestrates the video generation workflow idempotently."""
    logger.info(f"🚀 Starting workflow for Video ID: {video_id_str}")
    
    try:
        video_id = UUID(video_id_str)
    except ValueError:
        logger.error(f"❌ Invalid UUID: {video_id_str}")
        return

    # Use sync session for Celery task
    with get_sync_session() as session:
        job_service = VideoJobService(session)
        video = session.get(GeneratedVideo, video_id)
        
        if not video:
            logger.error(f"❌ Video {video_id} not found.")
            return

        def update_video_status(status: str, error_step: str = None, error_msg: str = None):
            """Update video status and error details."""
            video.status = status
            if error_msg:
                video.error_message = error_msg
                video.error_step = error_step
            session.add(video)
            session.commit()
            logger.info(f"📍 Video status updated: {status}")

        def get_resume_index() -> int:
            """Determine where to resume based on last successful step."""
            last_step = job_service.get_last_successful_step(video_id)
            if not last_step:
                return 0
            if last_step in PIPELINE_STEPS:
                return PIPELINE_STEPS.index(last_step) + 1
            return 0

        # Local imports
        try:
            from .api.v1.ai import generate_script
            from .schemas.ai_schema import AIScriptRequest
            from .services.video_generator import VideoGenerator
        except ImportError as e:
            logger.error(f"Error importing services: {e}")
            update_video_status("FAILED", "SETUP", f"Import error: {e}")
            return

        # Initialize shared state object (mocking persistence for now)
        scenes = []
        final_path = None

        resume_index = get_resume_index()
        
        # If we resume from SCRIPT_VALIDATED or later, we must have scenes
        # For Phase 2, we regenerate in-memory script if not SCRIPTING
        if resume_index > 0:
            logger.info("Restoring scenes for resume...")
            try:
                # In production, scenes would be read from DB or storage.
                # For Phase 2 fallback, generate them to keep memory state if needed.
                script_req = AIScriptRequest(
                    topic=video.topic or "Trending Topic",
                    template_id=video.template_id,
                    platform=video.platform
                )
                script_result = generate_script(script_req)
                scenes = [s.dict() for s in script_result.scenes] if script_result else []
            except Exception as e:
                pass


        try:
            for i in range(resume_index, len(PIPELINE_STEPS)):
                step_name = PIPELINE_STEPS[i]

                # Idempotency check
                if job_service.has_completed_step(video_id, step_name):
                    logger.info(f"⏭️ Skipping {step_name}, already completed.")
                    continue

                if step_name == "DONE":
                    update_video_status("DONE")
                    logger.info(f"🎉 Workflow fully completed for Video ID: {video_id}")
                    break

                # 🛡️ Step Isolation Protocol
                update_video_status(step_name)
                job = job_service.create_job(video_id, step_name)

                try:
                    logger.info(f"▶️ Running step: {step_name}")
                    
                    # Implementation logic for each step
                    if step_name == "SCRIPTING":
                        script_req = AIScriptRequest(
                            topic=video.topic or "Trending Topic",
                            template_id=video.template_id,
                            platform=video.platform
                        )
                        script_result = generate_script(script_req)
                        scenes = [s.dict() for s in script_result.scenes] if script_result else []
                    
                    elif step_name == "SCRIPT_VALIDATED":
                        if not scenes:
                            raise ValueError("No scenes available to validate")
                    
                    elif step_name == "MEDIA_COMPOSITION":
                        # Legacy handler: VideoGenerator() handles image, TTS & FFmpeg natively
                        # Next phases will break this down physically
                        
                        # Phase 3: Use deterministic storage key
                        canonical_key = build_storage_key(video, "final.mp4")
                        # Extract the inner path because VideoGenerator prepends 'videos/'
                        # videos/{user_id}/{video_id}/final.mp4 -> {user_id}/{video_id}/final.mp4
                        inner_path = canonical_key.replace("videos/", "", 1)
                        
                        final_path = VideoGenerator().assemble_video(scenes, output_filename=inner_path)
                        if final_path:
                            video.storage_key = final_path
                            session.add(video)
                            session.commit()
                            
                    elif step_name == "UPLOADING":
                        # Skip if storage key is already present/uploaded
                        pass
                        
                    elif step_name in ["IMAGE_GENERATION", "VOICE_SYNTHESIS", "ENCODING"]:
                        # Mocking steps since MEDIA_COMPOSITION does them for now
                        pass

                    job_service.mark_success(job.id)
                    logger.info(f"✅ Step {step_name} completed.")

                except Exception as step_error:
                    err_msg = str(step_error)
                    logger.error(f"❌ Step {step_name} failed: {err_msg}")
                    traceback.print_exc()

                    job_service.mark_failure(job.id, err_msg)
                    video.retry_count += 1
                    
                    if video.retry_count >= 3:
                        update_video_status("FAILED", step_name, err_msg)
                        logger.error(f"❌ Video {video_id} failed permanently after 3 retries.")
                        return  # Exit workflow
                    else:
                        # Allow celery to retry
                        update_video_status("QUEUED", step_name, err_msg)
                        session.commit()
                        raise self.retry(exc=step_error, countdown=60)

        except Exception as e:
            logger.error("Workflow aborted globally due to unhandled error.")
