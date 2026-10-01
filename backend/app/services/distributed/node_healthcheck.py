import asyncio
import logging
from typing import Callable, Optional
from datetime import datetime, timezone
import psutil # Note: requires psutil dependency

# For mocking GPU checks, since nvidia-smi bindings are heavy.
# Replace with pynvml in production.
def get_mock_gpu_stats():
    return {
        "gpu_name": "NVIDIA RTX 4090",
        "total_vram": 24576,
        "free_vram": 16000,
        "utilization": 30.5
    }

logger = logging.getLogger(__name__)

class NodeHealthCheck:
    """
    Runs on the worker node to periodically ping the central Redis registry.
    """
    def __init__(self, registry, node_id: str, capabilities: list, queue_types: list):
        self.registry = registry
        self.node_id = node_id
        self.capabilities = capabilities
        self.queue_types = queue_types
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def _health_loop(self):
        from .gpu_node_registry import GPUNode
        while self._running:
            try:
                gpu_stats = get_mock_gpu_stats() # Replace with actual probe
                
                node_data = GPUNode(
                    node_id=self.node_id,
                    hostname=psutil.os.uname().nodename if hasattr(psutil.os, 'uname') else "worker-node",
                    gpu_name=gpu_stats["gpu_name"],
                    total_vram=gpu_stats["total_vram"],
                    free_vram=gpu_stats["free_vram"],
                    utilization=gpu_stats["utilization"],
                    active_jobs=0, # Tracked via celery worker info ideally
                    status="ONLINE",
                    capabilities=self.capabilities,
                    queue_types=self.queue_types
                )
                
                await self.registry.register_node(node_data)
                
            except Exception as e:
                logger.error(f"[NodeHealthCheck] Failed to ping registry: {e}")
                
            await asyncio.sleep(15) # Ping every 15s

    async def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._health_loop())
            logger.info(f"[NodeHealthCheck] Started for {self.node_id}")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"[NodeHealthCheck] Stopped for {self.node_id}")
