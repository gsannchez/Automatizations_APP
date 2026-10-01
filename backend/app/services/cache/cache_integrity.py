import os
import subprocess
import logging

logger = logging.getLogger(__name__)

MIN_FILE_SIZE_BYTES = 50_000  # ~50KB minimum — anything smaller is corrupt

class CacheIntegrity:
    """
    Validates cached video clips before they are used in a render.
    Avoids silent corruption causing broken final exports.
    """

    @staticmethod
    def is_valid(video_path: str) -> bool:
        """
        Full integrity check:
        1. File exists and is not empty
        2. Minimum file size met
        3. ffprobe can read it without errors
        4. Duration > 0
        """
        if not os.path.exists(video_path):
            logger.warning(f"[CacheIntegrity] File not found: {video_path}")
            return False

        if os.path.getsize(video_path) < MIN_FILE_SIZE_BYTES:
            logger.warning(f"[CacheIntegrity] File too small (possible corrupt): {video_path}")
            return False

        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    video_path
                ],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                logger.warning(f"[CacheIntegrity] ffprobe error on {video_path}: {result.stderr.strip()}")
                return False

            duration = float(result.stdout.strip())
            if duration <= 0:
                logger.warning(f"[CacheIntegrity] Zero-duration file: {video_path}")
                return False

        except (ValueError, subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"[CacheIntegrity] Validation exception for {video_path}: {e}")
            return False

        return True

    @staticmethod
    def purge_corrupt(cache_dir: str) -> int:
        """
        Scans a cache directory, removes corrupt files, and returns count of removed files.
        """
        removed = 0
        if not os.path.isdir(cache_dir):
            return 0

        for fname in os.listdir(cache_dir):
            if not fname.endswith(".mp4"):
                continue
            full_path = os.path.join(cache_dir, fname)
            if not CacheIntegrity.is_valid(full_path):
                logger.warning(f"[CacheIntegrity] Purging corrupt file: {full_path}")
                os.remove(full_path)
                removed += 1

        logger.info(f"[CacheIntegrity] Purge complete. Removed {removed} corrupt files from {cache_dir}")
        return removed
