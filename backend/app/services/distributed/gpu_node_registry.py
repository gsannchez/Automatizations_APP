import json
import logging
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class GPUNode(BaseModel):
    node_id: str
    hostname: str
    gpu_name: str
    total_vram: int  # in MB
    free_vram: int   # in MB
    utilization: float # 0.0 to 100.0
    active_jobs: int
    status: str = "ONLINE" # ONLINE, OFFLINE, SAFE_MODE
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    capabilities: List[str] = Field(default_factory=list) # e.g. ["ai_video", "upscaling"]
    queue_types: List[str] = Field(default_factory=list)

class GPUNodeRegistry:
    """
    Registry for managing GPU nodes via Redis.
    Tracks VRAM, utilization, and node status.
    """
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "gpu_node:"
        self.expire_seconds = 60 # Auto expire nodes if no heartbeat

    async def register_node(self, node: GPUNode):
        """Update node heartbeat and metadata."""
        node.last_heartbeat = datetime.now(timezone.utc)
        data = node.json()
        await self.redis.set(f"{self.prefix}{node.node_id}", data, ex=self.expire_seconds)
        logger.debug(f"[GPUNodeRegistry] Node {node.node_id} heartbeat updated.")

    async def get_node(self, node_id: str) -> Optional[GPUNode]:
        data = await self.redis.get(f"{self.prefix}{node_id}")
        if data:
            return GPUNode.parse_raw(data)
        return None

    async def get_all_nodes(self) -> List[GPUNode]:
        """Fetch all active nodes from Redis."""
        keys = await self.redis.keys(f"{self.prefix}*")
        nodes = []
        for key in keys:
            data = await self.redis.get(key)
            if data:
                try:
                    nodes.append(GPUNode.parse_raw(data))
                except Exception as e:
                    logger.error(f"[GPUNodeRegistry] Failed to parse node data for {key}: {e}")
        return nodes

    async def remove_node(self, node_id: str):
        await self.redis.delete(f"{self.prefix}{node_id}")
        logger.info(f"[GPUNodeRegistry] Node {node_id} removed manually.")
