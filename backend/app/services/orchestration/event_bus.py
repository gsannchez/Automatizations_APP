"""Phase 8: Async Event Bus for inter-agent communication."""
import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import UUID

from app.utils.uuid_utils import generate_uuid7

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    TREND_DETECTED = "TREND_DETECTED"
    SCRIPT_READY = "SCRIPT_READY"
    RENDER_STARTED = "RENDER_STARTED"
    RENDER_COMPLETED = "RENDER_COMPLETED"
    VIDEO_UPLOADED = "VIDEO_UPLOADED"
    RETENTION_ANALYZED = "RETENTION_ANALYZED"
    TREND_SATURATED = "TREND_SATURATED"
    SYSTEM_OVERLOAD = "SYSTEM_OVERLOAD"
    CAMPAIGN_STARTED = "CAMPAIGN_STARTED"
    CAMPAIGN_EPISODE_DONE = "CAMPAIGN_EPISODE_DONE"
    AGENT_FAILED = "AGENT_FAILED"
    AGENT_RECOVERED = "AGENT_RECOVERED"
    GENERATION_LOOP_TICK = "GENERATION_LOOP_TICK"
    CHANNEL_CREATED = "CHANNEL_CREATED"
    VIRAL_SPIKE = "VIRAL_SPIKE"
    UNIVERSE_UPDATED = "UNIVERSE_UPDATED"
    CONTENT_RECYCLED = "CONTENT_RECYCLED"
    CHANNEL_SATURATED = "CHANNEL_SATURATED"
    PATTERN_DETECTED = "PATTERN_DETECTED"
    PATTERN_PROPAGATED = "PATTERN_PROPAGATED"
    CONTENT_BLOCKED = "CONTENT_BLOCKED"
    DIVERSITY_ALERT = "DIVERSITY_ALERT"
    UNIVERSE_EXPANDED = "UNIVERSE_EXPANDED"
    ARC_STARTED = "ARC_STARTED"
    ARC_COMPLETED = "ARC_COMPLETED"
    CHARACTER_EVOLVED = "CHARACTER_EVOLVED"
    LORE_UPDATED = "LORE_UPDATED"
    CROSSOVER_APPROVED = "CROSSOVER_APPROVED"
    VALUE_UPDATED = "VALUE_UPDATED"
    WASTE_DETECTED = "WASTE_DETECTED"
    RESOURCE_SHIFTED = "RESOURCE_SHIFTED"
    ECONOMIC_DECISION_MADE = "ECONOMIC_DECISION_MADE"
    CHANNEL_PROMOTED = "CHANNEL_PROMOTED"
    CHANNEL_DEMOTED = "CHANNEL_DEMOTED"
    UNIVERSE_FROZEN = "UNIVERSE_FROZEN"
    FORMAT_DEPRECATED = "FORMAT_DEPRECATED"
    RESOURCE_REALLOCATED = "RESOURCE_REALLOCATED"


@dataclass
class Event:
    event_type: EventType
    payload: Dict[str, Any]
    id: UUID = field(default_factory=generate_uuid7)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    max_retries: int = 3


class EventBus:
    """
    Lightweight async publish/subscribe event bus.
    Subscribers are coroutines keyed by EventType.
    Failed handlers are retried up to max_retries before going to the DLQ.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[EventType, List[Callable[[Event], Coroutine]]] = defaultdict(list)
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._dlq: List[Event] = []  # dead-letter queue
        self._running = False

    def subscribe(self, event_type: EventType, handler: Callable[[Event], Coroutine]) -> None:
        self._subscribers[event_type].append(handler)
        logger.debug(f"[EventBus] Subscribed handler '{handler.__name__}' to {event_type.value}")

    async def publish(self, event_type: EventType, payload: Dict[str, Any]) -> None:
        event = Event(event_type=event_type, payload=payload)
        await self._queue.put(event)
        logger.info(f"[EventBus] Published: {event_type.value} id={event.id}")

    async def _dispatch(self, event: Event) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        if not handlers:
            logger.debug(f"[EventBus] No handlers for {event.event_type.value}")
            return
        for handler in handlers:
            try:
                await handler(event)
            except Exception as exc:
                logger.warning(f"[EventBus] Handler '{handler.__name__}' failed: {exc}")
                if event.retry_count < event.max_retries:
                    event.retry_count += 1
                    await self._queue.put(event)
                    logger.info(f"[EventBus] Retry {event.retry_count}/{event.max_retries} for {event.event_type.value}")
                else:
                    self._dlq.append(event)
                    logger.error(f"[EventBus] DLQ: {event.event_type.value} id={event.id} after {event.max_retries} retries")

    async def run(self) -> None:
        self._running = True
        logger.info("[EventBus] Started.")
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch(event)
                self._queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.error(f"[EventBus] Unexpected error: {exc}", exc_info=True)

    def stop(self) -> None:
        self._running = False
        logger.info("[EventBus] Stopped.")

    def dlq_summary(self) -> List[Dict[str, Any]]:
        return [{"id": str(e.id), "type": e.event_type.value, "retries": e.retry_count, "ts": e.timestamp.isoformat()} for e in self._dlq]


# Module-level singleton
_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _bus
    if _bus is None:
        _bus = EventBus()
    return _bus
