"""
app/utils/media_utils.py

Helper functions for media metadata extraction.
"""
import os
import subprocess
import logging

logger = logging.getLogger(__name__)


def resolve_media_path(file_path: str) -> str:
    """Resolve a storage-relative or absolute path to a local filesystem path."""
    if os.path.isabs(file_path) and os.path.exists(file_path):
        return file_path
    try:
        from app.services.storage import storage
        return storage.get_local_path(file_path)
    except Exception:
        return file_path


def get_audio_duration(file_path: str) -> float:
    """Extracts duration of an audio file in seconds using ffprobe."""
    local_path = resolve_media_path(file_path)
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            local_path,
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.error("Failed to extract duration for %s: %s", file_path, e)
        return 5.0
