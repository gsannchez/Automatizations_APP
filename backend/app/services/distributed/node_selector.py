import logging
from typing import List, Optional
from .gpu_node_registry import GPUNodeRegistry, GPUNode

logger = logging.getLogger(__name__)

class NodeSelector:
    """
    Intelligently routes tasks to the most appropriate GPU node
    based on available VRAM, capabilities, and utilization.
    """
    def __init__(self, registry: GPUNodeRegistry):
        self.registry = registry

    def _score_node(self, node: GPUNode, required_vram: int) -> float:
        """
        Calculate a routing score. Higher is better.
        Returns -1.0 if the node cannot be selected.
        """
        if node.status != "ONLINE":
            return -1.0
        
        # 10% buffer
        if node.free_vram < required_vram * 1.1:
            return -1.0

        if node.utilization > 95.0:
            return -1.0

        # Score formula: Heavily favor free VRAM, penalize high utilization
        # Score ranges roughly from 0 to 100+
        vram_score = (node.free_vram / max(1, node.total_vram)) * 50
        util_score = ((100 - node.utilization) / 100) * 50
        
        return vram_score + util_score

    async def select_best_node(self, required_vram: int, required_capability: Optional[str] = None) -> Optional[GPUNode]:
        """Find the optimal node for a given workload constraint."""
        nodes = await self.registry.get_all_nodes()
        
        if not nodes:
            logger.warning("[NodeSelector] No active GPU nodes found.")
            return None

        best_node = None
        best_score = -1.0

        for node in nodes:
            if required_capability and required_capability not in node.capabilities:
                continue
                
            score = self._score_node(node, required_vram)
            if score > best_score:
                best_score = score
                best_node = node

        if best_node:
            logger.info(f"[NodeSelector] Selected {best_node.node_id} with score {best_score:.1f} for {required_vram}MB request.")
        else:
            logger.warning(f"[NodeSelector] No suitable node found for {required_vram}MB request.")
            
        return best_node
