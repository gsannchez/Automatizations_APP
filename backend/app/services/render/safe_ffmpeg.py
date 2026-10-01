import subprocess
import logging
from .render_recovery import RenderRecovery

logger = logging.getLogger(__name__)

class SafeFFmpeg:
    """
    Executes FFmpeg commands with strict timeouts, logging, and automatic fallback parsing.
    """
    
    @staticmethod
    def run(cmd: list, timeout: int = 600) -> bool:
        """
        Runs an FFmpeg command safely. Returns True if successful.
        """
        logger.info(f"Running SafeFFmpeg: {' '.join(cmd)}")
        try:
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            if process.returncode != 0:
                logger.error(f"FFmpeg failed with exit code {process.returncode}")
                logger.error(f"FFmpeg stderr: {process.stderr}")
                # Attempt recovery
                return RenderRecovery.attempt_fallback(cmd)
                
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg execution timed out after {timeout} seconds.")
            return False
        except Exception as e:
            logger.error(f"FFmpeg execution error: {e}")
            return False
