import sys
from pathlib import Path
import time
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo
from uuid import UUID

VID = "019e8452-6747-77ba-8d48-c2f47d92afec"
TIMEOUT = 60 * 15  # 15 minutes
INTERVAL = 10
start = time.time()

print(f"Polling video {VID} for up to {TIMEOUT} seconds...")

while time.time() - start < TIMEOUT:
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, UUID(VID))
        if not video:
            print(f"[{datetime.utcnow()}] Video not found yet")
        else:
            print(f"[{datetime.utcnow()}] status={video.status} pipeline_state={video.pipeline_state} progress={video.progress}")
            print(f"scenes: {None if not video.scenes_data else len(video.scenes_data)} scene_progress_keys: {None if not video.scene_progress else list(video.scene_progress.keys())}")
            if video.error_message:
                print(f"ERROR_STEP={video.error_step} ERROR_MSG={video.error_message}")
            if video.status == 'DONE' or video.status == 'FAILED':
                print('Terminal state reached, exiting poll loop.')
                break
    time.sleep(INTERVAL)

print('Polling finished.')
