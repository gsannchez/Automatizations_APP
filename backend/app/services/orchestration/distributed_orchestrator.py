"""
app/services/orchestration/distributed_orchestrator.py

Phase 9: Extends Master Orchestrator with cloud-native capabilities:
- Distributed event bus (via Redis Pub/Sub)
- Tenant isolation and quota checking
- Telemetry injection
- Smart scheduling hooks
"""
import json
import logging
from typing import Any, Dict

from .master_orchestrator import MasterOrchestrator
from ..scheduler.intelligent_scheduler import IntelligentScheduler
from ..tenancy.quota_manager import QuotaManager
from ..tenancy.tenant_context import TenantContext
from ..observability.tracing import TracingService

logger = logging.getLogger(__name__)


class DistributedOrchestrator(MasterOrchestrator):
    """
    Phase 9 Orchestrator. Wraps Phase 8 logic with:
    - Quota enforcement before scheduling
    - Telemetry span generation
    - Redis-based event bridging for multi-node orchestration
    """

    def __init__(
        self,
        session,
        redis_client,
        scheduler: IntelligentScheduler,
        quota_manager: QuotaManager,
    ):
        super().__init__(session)
        self.redis = redis_client
        self.smart_scheduler = scheduler
        self.quota_manager = quota_manager
        
        # Override Phase 8 generation loop with distributed awareness if needed
        # self.generation_loop = DistributedGenerationLoop(...)
        
        logger.info("[DistributedOrchestrator] Phase 9 cluster-aware orchestrator initialized.")

    async def schedule_content_distributed(
        self,
        trend_topic: str,
        platform: str,
        trend_score: float = 60.0,
        tenant_id: str = "default_tenant",
        tier: str = "free"
    ) -> Dict[str, Any]:
        """
        Drop-in replacement for schedule_content that respects tenant quotas
        and injects distributed tracing headers.
        """
        with TracingService.start_span("orchestrator.schedule_content") as span:
            span.set_attribute("tenant.id", tenant_id)
            span.set_attribute("platform", platform)
            
            # 1. Enforce Tenancy Quotas (Estimated 5 min GPU usage for a typical render)
            estimated_gpu_seconds = 300.0
            can_process = await self.quota_manager.can_process_task(
                tenant_id=tenant_id,
                tier=tier,
                estimated_seconds=estimated_gpu_seconds
            )
            
            if not can_process:
                logger.warning(f"[DistributedOrchestrator] Tenant {tenant_id} exceeded quota.")
                return {"error": "Quota exceeded", "status": "rejected"}

            # 2. Phase 8 compatibility: create DB record
            result = super().schedule_content(trend_topic, platform, trend_score)
            
            # 3. Phase 9: Smart Routing instead of blind Celery delay
            task_meta = {
                "task_name": "app.tasks.pipeline.run_full_generation",
                "kwargs": {
                    "schedule_id": result["scheduled_id"],
                    "tenant_id": tenant_id
                },
                "estimated_duration": estimated_gpu_seconds,
                "vram_mb": 6000
            }
            
            # The Smart Scheduler handles queue placement and target node pinning
            route = await self.smart_scheduler.schedule_task(task_meta)
            
            result["distributed_route"] = route
            return result

    async def broadcast_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """
        Phase 9: Send event across the entire Kubernetes cluster via Redis Pub/Sub,
        not just the local memory bus.
        """
        message = {
            "type": event_type,
            "payload": payload,
            "trace_id": TracingService.get_correlation_id()
        }
        await self.redis.publish("avm_cluster_events", json.dumps(message))
        
        # Local mirror
        from .event_bus import EventType
        try:
            enum_type = EventType(event_type)
            await self.bus.publish(enum_type, payload)
        except ValueError:
            pass  # Not a Phase 8 enum event
