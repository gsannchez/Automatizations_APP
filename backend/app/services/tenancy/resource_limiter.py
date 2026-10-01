import logging
from .tenant_context import TenantContext

logger = logging.getLogger(__name__)

class ResourceLimiter:
    """
    Enforces hard limits on active concurrency per tenant to prevent noisy neighbor issues.
    """
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "tenant_concurrency:"

    async def acquire_slot(self, tenant_id: str, max_concurrency: int) -> bool:
        """Attempt to acquire an execution slot using Redis."""
        key = f"{self.prefix}{tenant_id}"
        
        # Redis Lua script for atomic check-and-increment
        script = """
        local current = tonumber(redis.call('get', KEYS[1]) or '0')
        if current < tonumber(ARGV[1]) then
            redis.call('incr', KEYS[1])
            redis.call('expire', KEYS[1], 3600) -- Fail-safe expiration
            return 1
        else
            return 0
        end
        """
        result = await self.redis.eval(script, 1, key, max_concurrency)
        return result == 1

    async def release_slot(self, tenant_id: str):
        key = f"{self.prefix}{tenant_id}"
        await self.redis.decr(key)


class BillingMetrics:
    """
    Aggregates tenant usage for billing cycles.
    """
    def __init__(self, usage_tracker):
        self.tracker = usage_tracker

    async def generate_invoice_data(self, tenant_id: str) -> dict:
        """Generate a summary of usage for billing."""
        gpu_secs = await self.tracker.get_gpu_seconds(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "gpu_minutes": round(gpu_secs / 60.0, 2),
            # Stubbed metrics
            "storage_gb": 0.0,
            "api_calls": 0
        }
