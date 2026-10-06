"""Shared enums for the video pipeline."""
from enum import Enum


class PipelineState(str, Enum):
    """States of the video generation pipeline.

    The values MUST match the PostgreSQL enum ``pipelinestate`` created in
    migration ``ebe3bf76544b`` — keep them in sync.

    Inherits from ``str`` on purpose: the pipeline code compares the column
    both against the enum member (``video.pipeline_state != PipelineState.QUEUED``)
    and against its raw value (``== PipelineState.SCRIPTING.value``).
    """

    QUEUED = "QUEUED"
    SCRIPTING = "SCRIPTING"
    VALIDATED = "VALIDATED"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    AUDIO_GENERATION = "AUDIO_GENERATION"
    MEDIA_COMPOSITION = "MEDIA_COMPOSITION"
    ENCODING = "ENCODING"
    UPLOADING = "UPLOADING"
    DONE = "DONE"
    FAILED = "FAILED"
