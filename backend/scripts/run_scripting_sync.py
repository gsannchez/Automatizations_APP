import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.tasks.scripting import scripting_task
from app.core.database import get_sync_session
from app.models.generated_video import GeneratedVideo
from uuid import UUID

VID = '019e8452-6747-77ba-8d48-c2f47d92afec'

try:
    print('Running scripting_task.run synchronously...')
    res = scripting_task.run(VID)
    print('scripting_task returned:', res)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('Exception:', e)

# Inspect video after run
with get_sync_session() as session:
    video = session.get(GeneratedVideo, UUID(VID))
    print('After run status=', video.status)
    print('scenes_data=', video.scenes_data)
    print('error_message=', video.error_message)
    print('error_step=', video.error_step)
