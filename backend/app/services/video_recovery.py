"""Recover or fail videos interrupted by API restarts."""
import logging
from uuid import UUID

from sqlalchemy import text
from sqlmodel import Session

from app.core.config import settings
from app.core.database import sync_engine
from app.models.generated_video import GeneratedVideo, PipelineState

logger = logging.getLogger(__name__)

TERMINAL = {PipelineState.DONE.value, PipelineState.FAILED.value}

# Only resume work that was actively processing — never auto-start plain QUEUED rows
RESUMABLE_STATES = (
    PipelineState.SCRIPTING.value,
    PipelineState.VALIDATED.value,
    PipelineState.IMAGE_GENERATION.value,
    PipelineState.AUDIO_GENERATION.value,
    PipelineState.MEDIA_COMPOSITION.value,
    PipelineState.ENCODING.value,
    PipelineState.UPLOADING.value,
)


def recover_videos_on_startup() -> dict:
    """Optionally re-queue videos interrupted mid-pipeline (not idle QUEUED)."""
    stats = {"requeued": 0, "marked_failed": 0}

    if not settings.VIDEO_STARTUP_REQUEUE:
        logger.info(
            "VIDEO_STARTUP_REQUEUE=false — no se reencolan vídeos al arrancar la API"
        )
        return stats

    from app.services.health.celery_health import get_celery_worker_status

    worker = get_celery_worker_status()
    if not worker.get("available"):
        logger.warning(
            "VIDEO_STARTUP_REQUEUE=true pero no hay worker Celery — "
            "omitiendo re-queue (los vídeos quedarían en cola sin consumir)"
        )
        return stats

    with Session(sync_engine) as session:
        if settings.VIDEO_STARTUP_MARK_STUCK_FAILED:
            fail_sql = text("""
                UPDATE video
                SET status = 'FAILED',
                    pipeline_state = 'FAILED',
                    error_step = 'STUCK',
                    error_message = 'Video stuck too long without completing'
                WHERE is_deleted = false
                  AND pipeline_state NOT IN ('DONE', 'FAILED')
                  AND updated_at < now() - make_interval(mins => :mins)
            """)
            result = session.execute(
                fail_sql, {"mins": settings.VIDEO_STUCK_FAILED_MINUTES}
            )
            stats["marked_failed"] = result.rowcount or 0
            session.commit()

        placeholders = ", ".join(f"'{s}'" for s in RESUMABLE_STATES)
        rows = session.execute(
            text(f"""
                SELECT id::text AS id, pipeline_state::text AS pipeline_state
                FROM video
                WHERE is_deleted = false
                  AND status NOT IN ('DONE', 'FAILED')
                  AND pipeline_state NOT IN ('DONE', 'FAILED', 'QUEUED')
                  AND pipeline_state IN ({placeholders})
            """)
        ).fetchall()

        from app.tasks.pipeline import process_video_workflow

        for row in rows:
            video_id = row.id
            state = row.pipeline_state
            video = session.get(GeneratedVideo, UUID(video_id))
            if not video:
                continue

            if state in TERMINAL or state == PipelineState.QUEUED.value:
                continue
            if video.status in ("DONE", "FAILED"):
                continue

            video.error_message = None
            video.error_step = None
            session.add(video)
            session.commit()

            try:
                process_video_workflow.delay(video_id)
                stats["requeued"] += 1
                logger.info("Re-queued video %s (pipeline=%s)", video_id, state)
            except Exception as exc:
                logger.warning("Could not re-queue video %s: %s", video_id, exc)

    return stats
