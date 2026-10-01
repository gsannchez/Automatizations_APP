import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import get_sync_session
from uuid import UUID

vid='019e844e-0a5e-7b18-9236-47842dd84df4'
with get_sync_session() as session:
    from app.models.generated_video import GeneratedVideo
    video = session.get(GeneratedVideo, UUID(vid))
    print('video found:', bool(video))
    if video:
        print('pipeline_state:', video.pipeline_state)
        print('scenes_data:', video.scenes_data)
        print('scene_progress:', video.scene_progress)
        print('status:', video.status)
        print('error_message:', video.error_message)
        print('error_step:', video.error_step)
