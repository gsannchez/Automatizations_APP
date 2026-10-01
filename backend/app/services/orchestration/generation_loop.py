"""Phase 8: Continuous Generation Loop — autonomous, throttled content factory."""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from .event_bus import EventBus, EventType, get_event_bus
from .resource_planner import ResourcePlanner
from .decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

TICK_INTERVAL_SECONDS = 60          # Check every minute
MAX_CONCURRENT_GENERATIONS = 3      # Max pipelines in-flight at once
THROTTLE_ON_OVERLOAD = True


class GenerationLoop:
    """
    Infinite async loop that periodically ticks, evaluates system state,
    and fires the appropriate events to launch generation pipelines.
    Supports graceful shutdown and safe throttling.
    """

    def __init__(
        self,
        bus: Optional[EventBus] = None,
        tick_interval: int = TICK_INTERVAL_SECONDS,
    ) -> None:
        self.bus = bus or get_event_bus()
        self.resource_planner = ResourcePlanner()
        self.decision_engine = DecisionEngine()
        self.tick_interval = tick_interval
        self._running = False
        self._active_generations = 0
        self._tick_count = 0

    async def _tick(self) -> None:
        self._tick_count += 1
        logger.info(f"[GenerationLoop] Tick #{self._tick_count} @ {datetime.utcnow().isoformat()}")

        # 1. Check system resources
        health = self.resource_planner.evaluate()
        if health.safe_mode and THROTTLE_ON_OVERLOAD:
            logger.warning("[GenerationLoop] System overloaded. Throttling this tick.")
            await self.bus.publish(EventType.SYSTEM_OVERLOAD, {"render_tier": health.render_tier})
            return

        # 2. Check active generation ceiling
        if self._active_generations >= MAX_CONCURRENT_GENERATIONS:
            logger.info(f"[GenerationLoop] Max concurrent generations reached ({MAX_CONCURRENT_GENERATIONS}). Skipping tick.")
            return

        # 3. Get a decision plan
        plan = self.decision_engine.evaluate(top_trend_score=70.0, saturation_ratio=0.2)

        # 4. Fire TREND_DETECTED event to kick off the pipeline
        payload: Dict[str, Any] = {
            "tick": self._tick_count,
            "platform": plan.platform,
            "style": plan.style,
            "render_tier": plan.render_tier,
            "ai_video_allowed": plan.ai_video_allowed,
            "estimated_roi": plan.estimated_roi,
            "ts": datetime.utcnow().isoformat(),
        }
        await self.bus.publish(EventType.GENERATION_LOOP_TICK, payload)
        self._active_generations += 1
        logger.info(f"[GenerationLoop] Generation tick fired. In-flight: {self._active_generations}")

    def on_render_completed(self) -> None:
        """Call this when a render pipeline finishes to free the generation slot."""
        self._active_generations = max(0, self._active_generations - 1)
        logger.info(f"[GenerationLoop] Render completed. In-flight: {self._active_generations}")

    async def run_forever(self) -> None:
        self._running = True
        logger.info(f"[GenerationLoop] Starting. Tick interval: {self.tick_interval}s")
        # Start the event bus alongside
        asyncio.create_task(self.bus.run())
        while self._running:
            try:
                await self._tick()
            except Exception as exc:
                logger.error(f"[GenerationLoop] Error in tick: {exc}", exc_info=True)
            await asyncio.sleep(self.tick_interval)

    def stop(self) -> None:
        self._running = False
        self.bus.stop()
        logger.info("[GenerationLoop] Stopped.")

    def status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "tick_count": self._tick_count,
            "active_generations": self._active_generations,
            "max_concurrent": MAX_CONCURRENT_GENERATIONS,
            "tick_interval_secs": self.tick_interval,
        }
