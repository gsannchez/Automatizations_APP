import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Enable eager mode for synchronous task execution
import os
os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'true'
os.environ['CELERY_TASK_EAGER_PROPAGATES'] = 'true'

from app.tasks.pipeline import process_video_workflow
from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo
from uuid import UUID
import traceback

VID = '019e8464-9dca-7aec-b29b-dfdd0de4195a'

try:
    print(f"Running process_video_workflow synchronously for {VID}...")
    result = process_video_workflow.run(VID)
    print(f"Result: {result}")
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()

# Check video status after
with get_sync_session() as session:
    video = session.get(GeneratedVideo, UUID(VID))
    print(f"\nAfter run:")
    print(f"  status={video.status}")
    print(f"  pipeline_state={video.pipeline_state}")
    print(f"  scenes_data={bool(video.scenes_data)}")
    print(f"  error_message={video.error_message}")
    print(f"  error_step={video.error_step}")
