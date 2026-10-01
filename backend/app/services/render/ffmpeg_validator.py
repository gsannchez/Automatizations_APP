import os
import logging

logger = logging.getLogger(__name__)

class FFmpegValidator:
    """
    Validates FFmpeg inputs before attempting a heavy render.
    Prevents crashing halfway through a 10-minute render.
    """
    @staticmethod
    def validate_inputs(inputs: list) -> bool:
        """
        Checks if all '-i' paths exist.
        """
        for i, val in enumerate(inputs):
            if val == "-i" and i + 1 < len(inputs):
                file_path = inputs[i+1]
                if not os.path.exists(file_path):
                    logger.error(f"FFmpeg Validation failed: Input file not found -> {file_path}")
                    return False
        return True
