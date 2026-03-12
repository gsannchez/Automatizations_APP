"""Progress calculation utility.

Derives progress percentage from video status to ensure consistency
and eliminate manual progress tracking errors.
"""
from typing import Optional


# Progress mapping for each video status
PROGRESS_MAP = {
    "QUEUED": 0,
    "SCRIPTING": 10,
    "SCRIPT_VALIDATED": 20,
    "IMAGE_GENERATION": 40,
    "VOICE_SYNTHESIS": 60,
    "MEDIA_COMPOSITION": 75,
    "ENCODING": 85,
    "UPLOADING": 95,
    "DONE": 100,
}


def get_progress_from_status(status: str) -> int:
    """Derive progress percentage from video status.
    
    Args:
        status: Video status string (e.g., "ENCODING", "DONE")
        
    Returns:
        int: Progress percentage (0-100)
        
    Note:
        For FAILED status, returns 0 as progress cannot be determined
        from status alone. Caller should use last known progress if needed.
    """
    return PROGRESS_MAP.get(status, 0)
