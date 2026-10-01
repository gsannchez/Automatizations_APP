"""Fixed final MP4 copied into media/ for download."""
import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_PUBLISHED_SOURCE = _BACKEND_DIR.parent / "videos" / "video_20260602011800_7f3a9b2e.mp4"
PUBLISHED_MEDIA_NAME = "final_export.mp4"
PUBLISHED_DOWNLOAD_BASENAME = "video_20260602011800_7f3a9b2e.mp4"


def _transcode_to_h264(src: Path, dest: Path) -> bool:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return False
    try:
        subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(src),
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "23",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(dest),
            ],
            check=True,
            capture_output=True,
            timeout=180,
        )
        return True
    except Exception as exc:
        logger.warning("ffmpeg transcode failed, using raw copy: %s", exc)
        return False


def ensure_published_final_video() -> None:
    dest = _BACKEND_DIR / "media" / PUBLISHED_MEDIA_NAME
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not _PUBLISHED_SOURCE.is_file():
        logger.warning("Published video source missing: %s", _PUBLISHED_SOURCE)
        return
    if dest.is_file() and dest.stat().st_mtime >= _PUBLISHED_SOURCE.stat().st_mtime:
        return
    if _transcode_to_h264(_PUBLISHED_SOURCE, dest):
        logger.info("Published final video transcoded to H.264: %s", dest)
        return
    shutil.copy2(_PUBLISHED_SOURCE, dest)
