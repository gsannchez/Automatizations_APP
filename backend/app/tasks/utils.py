import logging
from sqlmodel import Session
from ..models.generated_video import GeneratedVideo

logger = logging.getLogger(__name__)

# Legacy videostatus names still used by progress_utils / frontend fallbacks
PIPELINE_TO_LEGACY_STATUS = {
    "VALIDATED": "SCRIPT_VALIDATED",
    "AUDIO_GENERATION": "VOICE_SYNTHESIS",
}


def to_legacy_status(pipeline_state: str) -> str:
    return PIPELINE_TO_LEGACY_STATUS.get(pipeline_state, pipeline_state)


def update_video_status(session: Session, video: GeneratedVideo, new_state: str, progress: int = None, error_step: str = None, error_msg: str = None):
    """Actualiza el estado, progreso y errores del video de manera unificada."""
    old_state = video.pipeline_state.value if hasattr(video.pipeline_state, 'value') else video.pipeline_state

    video.pipeline_state = new_state
    video.status = to_legacy_status(new_state) if new_state != "FAILED" else "FAILED"

    if progress is not None:
        video.progress = progress

    if error_msg:
        video.error_message = error_msg
        video.error_step = error_step or new_state

    session.add(video)
    session.commit()

    if old_state != new_state:
        logger.info("State transition %s -> %s (video %s)", old_state, new_state, video.id)
