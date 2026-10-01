import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import get_sync_session
from app.models.template import Template
from app.models.generated_video import GeneratedVideo
from app.tasks import process_video_workflow
import uuid

# Create template and video, then queue the workflow
with get_sync_session() as session:
    template = Template(name="AutoTest Template", platform="YouTube", structure_json='[{"text":"Intro","duration":5}]')
    session.add(template)
    session.flush()
    session.refresh(template)

    video = GeneratedVideo(template_id=template.id, title="Automated Test Video", platform="YouTube", user_id=None)
    session.add(video)
    session.flush()
    session.refresh(video)

    print("Created video id:", str(video.id))
    # Ensure video is queued (reset any RESTART cleanup) before enqueueing
    from app.models.generated_video import PipelineState
    video.status = "QUEUED"
    video.pipeline_state = PipelineState.QUEUED
    video.progress = 0
    video.error_message = None
    video.error_step = None
    session.add(video)
    session.commit()

    # Enqueue Celery workflow
    process_video_workflow.delay(str(video.id))
    print("Enqueued process_video_workflow for:", str(video.id))
