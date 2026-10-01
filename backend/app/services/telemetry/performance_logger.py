import logging
import time
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class PerformanceLogger:
    """
    Tracks and logs execution times and resource peaks for observability.
    """
    
    @staticmethod
    @contextmanager
    def trace(operation_name: str):
        """Context manager to trace execution time of operations."""
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"[TRACE] {operation_name} took {duration:.2f} seconds.")
            # In a real system, send this to Datadog / Prometheus / DB
