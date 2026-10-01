import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo
from uuid import UUID

if len(sys.argv) < 2:
    print('Usage: check_video_status.py <video_id>')
    sys.exit(1)

VID = sys.argv[1]
with get_sync_session() as session:
    video = session.get(GeneratedVideo, UUID(VID))
    if not video:
        print('Video not found')
    else:
        print('id=', video.id)
        print('status=', video.status)
        print('pipeline_state=', video.pipeline_state)
        print('progress=', video.progress)
        print('error_step=', video.error_step)
        print('error_message=', video.error_message)
        print('scenes_data=', bool(video.scenes_data))
