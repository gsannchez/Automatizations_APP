"""
app/services/recovery_distributed/node_failover.py

Detects GPU node failures and migrates active jobs to healthy nodes.
"""
import logging
from typing import Any, Dict, List, Optional

from ..distributed.gpu_node_registry import GPUNode, GPUNodeRegistry
from ..distributed.node_selector import NodeSelector

logger = logging.getLogger(__name__)


class NodeFailover:
    """
    Monitors the GPU node registry for nodes that have dropped offline
    and coordinates migration of their workloads to healthy alternatives.
    """

    def __init__(self, registry: GPUNodeRegistry, celery_app):
        self.registry = registry
        self.celery = celery_app
        self.selector = NodeSelector(registry)

    async def run_failover_check(self) -> Dict[str, Any]:
        """
        1. List all nodes from registry (already filtered to alive by Redis TTL).
        2. Compare against a known-active node set stored in a separate Redis key.
        3. For any node that disappeared, trigger workload migration.
        """
        current_nodes = await self.registry.get_all_nodes()
        current_ids = {n.node_id for n in current_nodes}

        failed_nodes = await self._detect_failed_nodes(current_ids)
        migrations: List[Dict] = []

        for failed_id in failed_nodes:
            result = await self._migrate_node_workload(failed_id, current_nodes)
            migrations.append(result)

        await self._update_known_nodes(current_ids)

        return {"failed_nodes": list(failed_nodes), "migrations": migrations}

    async def _detect_failed_nodes(self, current_ids: set) -> set:
        """Compare current live nodes against previously known nodes."""
        raw = await self.registry.redis.smembers("known_gpu_nodes")
        known_ids = {v.decode() if isinstance(v, bytes) else v for v in raw}
        failed = known_ids - current_ids
        if failed:
            logger.warning(f"[NodeFailover] Detected failed node(s): {failed}")
        return failed

    async def _update_known_nodes(self, current_ids: set) -> None:
        """Persist the current live node set for next comparison."""
        pipe = self.registry.redis.pipeline()
        pipe.delete("known_gpu_nodes")
        if current_ids:
            pipe.sadd("known_gpu_nodes", *current_ids)
        pipe.expire("known_gpu_nodes", 300)
        await pipe.execute()

    async def _migrate_node_workload(
        self, failed_node_id: str, available_nodes: List[GPUNode]
    ) -> Dict[str, Any]:
        """
        Identify tasks that were targeted at the failed node and
        requeue them with a hint toward a healthy alternative.
        """
        try:
            # Look up jobs that had this node as target (stored per-task in Redis)
            job_keys = await self.registry.redis.keys(
                f"task_node_affinity:{failed_node_id}:*"
            )
            requeued_count = 0

            for key in job_keys:
                raw = await self.registry.redis.get(key)
                if not raw:
                    continue

                import json
                task_meta = json.loads(raw)
                task_name = task_meta.get("task_name", "unknown")
                kwargs = task_meta.get("kwargs", {})
                queue = task_meta.get("queue", "recovery_queue")

                # Find a replacement node
                replacement = await self.selector.select_best_node(
                    required_vram=task_meta.get("vram_mb", 4000)
                )
                if replacement:
                    kwargs["_target_node"] = replacement.node_id

                kwargs["_is_recovery"] = True
                sig = self.celery.signature(task_name, kwargs=kwargs, queue=queue)
                sig.apply_async()

                await self.registry.redis.delete(key)
                requeued_count += 1

            logger.info(
                f"[NodeFailover] Migrated {requeued_count} job(s) from dead node {failed_node_id}"
            )
            return {"node": failed_node_id, "requeued": requeued_count}

        except Exception as exc:
            logger.error(
                f"[NodeFailover] Migration error for node {failed_node_id}: {exc}"
            )
            return {"node": failed_node_id, "requeued": 0, "error": str(exc)}
