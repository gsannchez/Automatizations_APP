import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo
from uuid import UUID

VID = "019e8464-9dca-7aec-b29b-dfdd0de4195a"

for i in range(60):
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, UUID(VID))
        if video:
            print(f"[{i:2d}] status={video.status:10} pipeline={str(video.pipeline_state):30} progress={video.progress} error={video.error_step or 'None'}")
        else:
            print(f"[{i:2d}] Video not found")
    time.sleep(2)
