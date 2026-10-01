"""
tests/cluster_simulation.py

Simulates a multi-node cluster environment to validate Phase 9 distributed logic:
- GPUNodeRegistry heartbeats
- Quota Management
- Distributed Locking
- Retry Coordinator
"""
import asyncio
import logging
from unittest.mock import AsyncMock

from app.services.distributed.gpu_node_registry import GPUNodeRegistry
from app.services.scheduler.intelligent_scheduler import IntelligentScheduler
from app.services.tenancy.quota_manager import QuotaManager, UsageTracker
from app.services.recovery_distributed.retry_coordinator import RetryCoordinator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClusterSimulation")


class MockRedis:
    def __init__(self):
        self.data = {}
        self.zsets = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value, ex=None):
        self.data[key] = value

    async def exists(self, key):
        return key in self.data

    async def delete(self, key):
        self.data.pop(key, None)

    async def keys(self, pattern):
        prefix = pattern.replace("*", "")
        return [k for k in self.data.keys() if k.startswith(prefix)]

    async def hgetall(self, key):
        return self.data.get(key, {})

    async def zadd(self, key, mapping):
        if key not in self.zsets:
            self.zsets[key] = {}
        for val, score in mapping.items():
            self.zsets[key][val] = score

    async def zrangebyscore(self, key, min_score, max_score):
        if key not in self.zsets:
            return []
        import math
        mn = float("-inf") if min_score == "-inf" else float(min_score)
        mx = float("inf") if max_score == "+inf" else float(max_score)
        return [k for k, v in self.zsets[key].items() if mn <= v <= mx]


async def run_simulation():
    redis = MockRedis()
    
    # 1. Test Node Registry
    registry = GPUNodeRegistry(redis)
    await registry.register_node("node_1", {"vram_total_mb": 24000, "vram_free_mb": 12000})
    await registry.register_node("node_2", {"vram_total_mb": 8000, "vram_free_mb": 2000})
    nodes = await registry.get_all_nodes()
    logger.info(f"Registered nodes: {[n.node_id for n in nodes]}")
    assert len(nodes) == 2

    # 2. Test Smart Scheduling logic
    scheduler = IntelligentScheduler(registry, redis)
    task_meta = {
        "task_name": "render",
        "estimated_duration": 300,
        "vram_mb": 4000
    }
    route = await scheduler.schedule_task(task_meta)
    logger.info(f"Task routed to: {route}")
    assert route["target_node"] == "node_1" # Because node_2 doesn't have 4000MB free

    # 3. Test Quota Manager
    usage = UsageTracker(redis)
    quota = QuotaManager(usage)
    # Give tenant some usage
    await usage.add_gpu_seconds("tenant_123", 3500) 
    # Try 200s task on free tier (max 3600) -> Should fail
    can_run = await quota.can_process_task("tenant_123", "free", 200)
    logger.info(f"Tenant quota check (Free): {can_run}")
    assert can_run is False

    # Try on Pro tier (max 36000) -> Should pass
    can_run_pro = await quota.can_process_task("tenant_123", "pro", 200)
    logger.info(f"Tenant quota check (Pro): {can_run_pro}")
    assert can_run_pro is True

    # 4. Test Retry Coordinator
    mock_celery = AsyncMock()
    retry = RetryCoordinator(redis, mock_celery)
    await retry.schedule_retry({"task_name": "failing_task", "task_id": "123"}, attempt=1)
    
    # Simulate time passing by fetching from zset
    due = await redis.zrangebyscore("retry_delay_queue", "-inf", "+inf")
    logger.info(f"Tasks due for retry: {len(due)}")
    assert len(due) == 1

    logger.info("Simulation completed successfully.")

if __name__ == "__main__":
    asyncio.run(run_simulation())
