from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo, PipelineState
from app.models.user import User
from app.models.template import Template
from sqlmodel import select
from app.models.generated_video import GeneratedVideo, PipelineState
from sqlmodel import select

with get_sync_session() as session:
    videos = session.execute(select(GeneratedVideo)).scalars().all()
    count = 0
    for v in videos:
        if v.pipeline_state in [PipelineState.FAILED, PipelineState.SCRIPTING]:
            v.pipeline_state = PipelineState.QUEUED
            v.status = PipelineState.QUEUED.value
            count += 1
    session.commit()
    print(f'Reset {count} videos to QUEUED')
