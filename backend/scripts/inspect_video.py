from app.core.database import get_sync_session
from uuid import UUID

vid='019e844e-0a5e-7b18-9236-47842dd84df4'
with get_sync_session() as session:
    video = session.get(__import__('app').models.generated_video.GeneratedVideo, UUID(vid))
    print('video found:', bool(video))
    if video:
        print('pipeline_state:', video.pipeline_state)
        print('scenes_data:', video.scenes_data)
        print('scene_progress:', video.scene_progress)
        print('status:', video.status)
