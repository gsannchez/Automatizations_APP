import gc
import logging

logger = logging.getLogger(__name__)


class CUDACleanup:
    """
    Aggressive memory cleanup to avoid fragmentation and leaks.
    """

    @staticmethod
    def force_cleanup() -> None:
        """Run gc and release cached CUDA blocks.

        ``torch`` is imported lazily on purpose: this module sits on the API's
        import path (via the composition task), and importing torch there would
        pull ~200 MB into the web process just to serve HTTP.
        """
        gc.collect()
        try:
            import torch
        except ImportError:
            return

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
