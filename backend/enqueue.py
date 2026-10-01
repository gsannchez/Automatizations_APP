from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo, PipelineState
from app.models.user import User
from app.models.template import Template
from sqlmodel import select
from app.tasks.pipeline import process_video_workflow

with get_sync_session() as session:
    videos = session.execute(select(GeneratedVideo).where(GeneratedVideo.pipeline_state == PipelineState.QUEUED)).scalars().all()
    for v in videos:
        process_video_workflow.delay(str(v.id))
        print(f'Re-enqueued {v.id}')
