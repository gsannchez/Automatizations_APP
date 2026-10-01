from .pipeline import process_video_workflow
from .scripting import scripting_task, validate_task
from .image_generation import generate_image_task
from .audio_generation import generate_audio_task
from .composition import compose_video_task
from .encoding import encode_video_task
from .upload import upload_task

from ..services.video_job_service import VideoJobService
from ..services.video_generator import VideoGenerator
from ..services.script_generator import ScriptGenerator

PIPELINE_STEPS = [
    "SCRIPTING",
    "VALIDATED",
    "IMAGE_GENERATION",
    "AUDIO_GENERATION",
    "MEDIA_COMPOSITION",
    "ENCODING",
    "UPLOADING",
    "DONE",
]


def generate_script(*args, **kwargs):
    return ScriptGenerator().generate(*args, **kwargs)
