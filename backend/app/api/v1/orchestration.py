"""Phase 8: Orchestration observability API endpoints."""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ...core.database import get_sync_session
from ...services.orchestration.master_orchestrator import MasterOrchestrator
from ...services.orchestration.campaign_manager import CampaignManager
from ...services.orchestration.content_scheduler import ContentScheduler
from ...services.orchestration.resource_planner import ResourcePlanner
from ...services.orchestration.analytics_feedback import AnalyticsFeedback

router = APIRouter(tags=["Orchestration"])
logger = logging.getLogger(__name__)


def _get_orchestrator(session: Session = Depends(get_sync_session)) -> MasterOrchestrator:
    return MasterOrchestrator(session)


@router.get("/status")
def orchestration_status(orch: MasterOrchestrator = Depends(_get_orchestrator)) -> Dict[str, Any]:
    """Full system status: agents, system health, generation loop, DLQ."""
    return orch.get_status()


@router.get("/agents")
def list_agents(orch: MasterOrchestrator = Depends(_get_orchestrator)) -> Dict[str, Any]:
    """List all agents and their current state/memory snapshots."""
    return {"agents": orch.get_agent_list()}


@router.get("/queue-health")
def queue_health(session: Session = Depends(get_sync_session)) -> Dict[str, Any]:
    """Pending content schedule items."""
    scheduler = ContentScheduler(session)
    pending = scheduler.get_pending(limit=20)
    return {
        "pending_count": len(pending),
        "items": [
            {
                "id": str(p.id),
                "platform": p.platform,
                "trend_topic": p.trend_topic,
                "priority": p.priority,
                "publish_time": p.publish_time.isoformat(),
                "predicted_score": p.predicted_score,
            }
            for p in pending
        ],
    }


@router.get("/system-load")
def system_load() -> Dict[str, Any]:
    """Real-time system resource snapshot."""
    planner = ResourcePlanner()
    return planner.to_dict()


@router.get("/decisions")
def latest_decision(orch: MasterOrchestrator = Depends(_get_orchestrator)) -> Dict[str, Any]:
    """Run the decision engine and return the latest DecisionPlan."""
    return orch.get_decisions()


@router.get("/campaigns")
def list_campaigns(session: Session = Depends(get_sync_session)) -> Dict[str, Any]:
    """List all active campaigns and their progress."""
    manager = CampaignManager(session)
    return {"campaigns": manager.list_campaigns()}


@router.post("/campaigns")
def create_campaign(
    name: str,
    total_episodes: int = 20,
    session: Session = Depends(get_sync_session),
) -> Dict[str, Any]:
    """Create a new episodic campaign."""
    manager = CampaignManager(session)
    campaign = manager.create_campaign(name=name, total_episodes=total_episodes)
    return {"id": str(campaign.id), "name": campaign.name, "total_episodes": campaign.total_episodes}


@router.post("/recover")
def trigger_recovery(orch: MasterOrchestrator = Depends(_get_orchestrator)) -> Dict[str, Any]:
    """Manually trigger a recovery sweep."""
    return orch.run_recovery()


@router.post("/feedback-cycle")
def run_feedback(session: Session = Depends(get_sync_session)) -> Dict[str, Any]:
    """Trigger an analytics feedback cycle to update style scores."""
    feedback = AnalyticsFeedback(session)
    return feedback.run_feedback_cycle()


@router.get("/schedule")
def get_full_schedule(session: Session = Depends(get_sync_session)) -> Dict[str, Any]:
    """Get full content schedule."""
    scheduler = ContentScheduler(session)
    return {"schedule": scheduler.list_all(limit=50)}

@router.get("/event-stream")
async def event_stream():
    """SSE endpoint for live orchestration events."""
    from sse_starlette.sse import EventSourceResponse
    from ...services.orchestration.event_bus import get_event_bus
    import asyncio
    
    bus = get_event_bus()
    
    async def event_generator():
        queue = asyncio.Queue()
        
        async def sse_handler(event):
            await queue.put(event)
            
        from ...services.orchestration.event_bus import EventType
        for event_type in EventType:
            bus.subscribe(event_type, sse_handler)
            
        try:
            while True:
                event = await queue.get()
                yield {
                    "event": event.event_type.value,
                    "id": str(event.id),
                    "data": str(event.payload)
                }
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
