import logging
import json
import traceback
import uuid
from datetime import datetime, timezone

class StructuredLogger:
    """
    Emits JSON-structured log entries with trace IDs, task IDs, and render IDs.
    Use this instead of `print()` or plain `logging.info()` in tasks.
    """

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _build_record(self, level: str, message: str, **kwargs) -> str:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **kwargs,
        }
        return json.dumps(record)

    def info(self, message: str, **kwargs):
        self._logger.info(self._build_record("INFO", message, **kwargs))

    def warning(self, message: str, **kwargs):
        self._logger.warning(self._build_record("WARNING", message, **kwargs))

    def error(self, message: str, exc: Exception = None, **kwargs):
        extra = {}
        if exc:
            extra["traceback"] = traceback.format_exc()
        self._logger.error(self._build_record("ERROR", message, **extra, **kwargs))

    def critical(self, message: str, **kwargs):
        self._logger.critical(self._build_record("CRITICAL", message, **kwargs))

    @staticmethod
    def new_trace_id() -> str:
        """Generate a new correlation/trace ID for a pipeline run."""
        return str(uuid.uuid4())
