import logging
from typing import Dict, Any
from .tenant_context import TenantContext

logger = logging.getLogger(__name__)

class UsageTracker:
    """
    Tracks resource usage (GPU minutes, storage) per tenant in Redis.
    """
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "tenant_usage:"

    async def add_gpu_seconds(self, tenant_id: str, seconds: float):
        """Atomically increment GPU usage."""
        key = f"{self.prefix}{tenant_id}:gpu_seconds"
        await self.redis.incrbyfloat(key, seconds)
        logger.debug(f"[UsageTracker] Added {seconds}s to {tenant_id}")

    async def get_gpu_seconds(self, tenant_id: str) -> float:
        val = await self.redis.get(f"{self.prefix}{tenant_id}:gpu_seconds")
        return float(val) if val else 0.0


class QuotaManager:
    """
    Enforces per-tenant limits and usage quotas.
    """
    QUOTAS = {
        "free": {"gpu_seconds": 3600},       # 1 hour/month
        "pro": {"gpu_seconds": 36000},       # 10 hours/month
        "enterprise": {"gpu_seconds": -1}    # Unlimited
    }

    def __init__(self, usage_tracker: UsageTracker):
        self.tracker = usage_tracker

    async def can_process_task(self, tenant_id: str, tier: str, estimated_seconds: float) -> bool:
        """Check if tenant has enough quota for the task."""
        limit = self.QUOTAS.get(tier, {}).get("gpu_seconds", 0)
        
        if limit == -1:
            return True # Unlimited
            
        current_usage = await self.tracker.get_gpu_seconds(tenant_id)
        
        if current_usage + estimated_seconds > limit:
            logger.warning(f"[QuotaManager] Tenant {tenant_id} exceeded GPU quota.")
            return False
            
        return True
