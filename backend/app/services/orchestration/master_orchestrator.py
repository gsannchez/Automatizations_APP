"""Phase 8: Master Orchestrator — coordinates all autonomous agents."""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Session

from ...models.orchestration import AgentState
from .agent_memory import AgentMemory
from .content_scheduler import ContentScheduler
from .decision_engine import DecisionEngine
from .event_bus import EventBus, EventType, get_event_bus
from .generation_loop import GenerationLoop
from .platform_strategy import PlatformStrategyEngine
from .recovery_manager import RecoveryManager
from .resource_planner import ResourcePlanner

logger = logging.getLogger(__name__)

AGENT_NAMES = [
    "TrendAgent",
    "IdeaAgent",
    "ScriptAgent",
    "RenderAgent",
    "AnalyticsAgent",
    "UploadAgent",
    "LearningAgent",
]


class MasterOrchestrator:
    """
    Top-level coordinator for the Phase 8 multi-agent system.
    Initialises all sub-agents, wires the event bus, and exposes
    status/control surfaces to the API layer.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.bus: EventBus = get_event_bus()
        self.resource_planner = ResourcePlanner()
        self.decision_engine = DecisionEngine()
        self.scheduler = ContentScheduler(session)
        self.recovery = RecoveryManager(session)
        self.platform_strategy = PlatformStrategyEngine()
        self.generation_loop = GenerationLoop(bus=self.bus)
        self._agent_memories: Dict[str, AgentMemory] = {
            name: AgentMemory(name, session) for name in AGENT_NAMES
        }
        self._register_bus_handlers()
        logger.info("[MasterOrchestrator] Initialized with agents: " + ", ".join(AGENT_NAMES))

    def _register_bus_handlers(self) -> None:
        """Wire internal event handlers to the bus."""
        self.bus.subscribe(EventType.SYSTEM_OVERLOAD, self._handle_overload)
        self.bus.subscribe(EventType.RENDER_COMPLETED, self._handle_render_completed)
        self.bus.subscribe(EventType.AGENT_FAILED, self._handle_agent_failed)
        self.bus.subscribe(EventType.CHANNEL_CREATED, self._handle_channel_created)
        self.bus.subscribe(EventType.VIRAL_SPIKE, self._handle_viral_spike)
        self.bus.subscribe(EventType.UNIVERSE_UPDATED, self._handle_universe_updated)
        self.bus.subscribe(EventType.CONTENT_RECYCLED, self._handle_content_recycled)
        self.bus.subscribe(EventType.CHANNEL_SATURATED, self._handle_channel_saturated)
        self.bus.subscribe(EventType.PATTERN_DETECTED, self._handle_pattern_detected)

    async def _handle_overload(self, event) -> None:
        logger.warning(f"[MasterOrchestrator] System overload received: {event.payload}")
        for name, mem in self._agent_memories.items():
            if mem.get_state() == AgentState.GENERATING:
                mem.set_state(AgentState.WAITING)

    async def _handle_render_completed(self, event) -> None:
        self.generation_loop.on_render_completed()
        render_agent_mem = self._agent_memories.get("RenderAgent")
        if render_agent_mem:
            render_agent_mem.set_state(AgentState.IDLE)
        logger.info(f"[MasterOrchestrator] Render completed: {event.payload}")

    async def _handle_agent_failed(self, event) -> None:
        agent_name = event.payload.get("agent")
        if agent_name and agent_name in self._agent_memories:
            self._agent_memories[agent_name].set_state(AgentState.FAILED)
            self._agent_memories[agent_name].record_error(str(event.payload.get("error", "unknown")))
        logger.error(f"[MasterOrchestrator] Agent failure: {event.payload}")

    async def _handle_channel_created(self, event) -> None:
        logger.info(f"[MasterOrchestrator] Channel created event: {event.payload}")

    async def _handle_viral_spike(self, event) -> None:
        logger.info(f"[MasterOrchestrator] Viral spike event: {event.payload}")

    async def _handle_universe_updated(self, event) -> None:
        logger.info(f"[MasterOrchestrator] Universe updated event: {event.payload}")
        # Phase 11.3 Expansion Pipeline
        from app.services.universe_engine.universe_expansion import UniverseExpansionEngine
        from app.services.universe_engine.character_memory import CharacterMemory
        from app.services.universe_engine.lore_tracker import LoreTracker
        
        expansion = UniverseExpansionEngine()
        char_mem = CharacterMemory()
        lore = LoreTracker()
        
        proposed_lore = event.payload.get("proposed_lore", "")
        character_id = event.payload.get("character_id")
        new_emotion = event.payload.get("new_emotion")
        
        # 1. Enforce character consistency
        if character_id and new_emotion:
            if not char_mem.maintain_emotional_continuity(character_id, new_emotion):
                await self.bus.publish(EventType.CONTENT_BLOCKED, {"reason": "character_inconsistency"})
                return
                
        # 2. Check lore conflicts
        if not lore.prevent_contradictions(proposed_lore, {}): # Mock existing lore
            await self.bus.publish(EventType.CONTENT_BLOCKED, {"reason": "lore_conflict"})
            return
            
        # 3. Expand Universe
        if expansion.evaluate_expansion(event.payload.get("new_arc", {}), []):
            await self.bus.publish(EventType.UNIVERSE_EXPANDED, {"universe_id": event.payload.get("universe_id")})


    async def _handle_content_recycled(self, event) -> None:
        logger.info(f"[MasterOrchestrator] Content recycled event: {event.payload}")

    async def _handle_channel_saturated(self, event) -> None:
        logger.info(f"[MasterOrchestrator] Channel saturated event: {event.payload}")

    async def _handle_pattern_detected(self, event) -> None:
        logger.info(f"[MasterOrchestrator] Pattern detected: {event.payload}")
        # Phase 11.2 logic
        from app.services.channel_network.cross_channel_intelligence import CrossChannelIntelligence
        from app.services.channel_network.contamination_guard import ContaminationGuard
        
        cci = CrossChannelIntelligence()
        cg = ContaminationGuard()
        
        pattern_data = event.payload.get("pattern")
        target_niche = event.payload.get("target_niche", "general")
        hook = event.payload.get("hook", "")
        
        if cg.detect_duplicate_hooks(hook, []):  # Mock past hooks
            await self.bus.publish(EventType.CONTENT_BLOCKED, {"reason": "duplicate_hook", "hook": hook})
            return
            
        weight = cci.assign_propagation_weight(pattern_data or {}, target_niche)
        if weight > 0.5:
            await self.bus.publish(EventType.PATTERN_PROPAGATED, {"pattern": pattern_data, "weight": weight})

    def set_agent_state(self, agent_name: str, state: AgentState) -> None:
        if agent_name in self._agent_memories:
            self._agent_memories[agent_name].set_state(state)

    def run_recovery(self) -> Dict[str, Any]:
        return self.recovery.full_recovery_sweep()

    def schedule_content(self, trend_topic: str, platform: str, trend_score: float = 60.0) -> Dict[str, Any]:
        sched = self.scheduler.schedule_item(trend_topic, platform, trend_score)
        return {
            "scheduled_id": str(sched.id),
            "publish_time": sched.publish_time.isoformat(),
            "platform": sched.platform,
            "priority": sched.priority,
        }

    def get_status(self) -> Dict[str, Any]:
        agent_snapshots = [mem.snapshot() for mem in self._agent_memories.values()]
        health = self.resource_planner.to_dict()
        loop_status = self.generation_loop.status()
        dlq = self.bus.dlq_summary()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "agents": agent_snapshots,
            "system_health": health,
            "generation_loop": loop_status,
            "event_bus_dlq": dlq,
        }

    def get_agent_list(self) -> List[Dict[str, Any]]:
        return [mem.snapshot() for mem in self._agent_memories.values()]

    def get_decisions(self) -> Dict[str, Any]:
        plan = self.decision_engine.evaluate()
        return self.decision_engine.to_dict(plan)
