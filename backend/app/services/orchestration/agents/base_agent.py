import asyncio
import logging
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

from ...models.orchestration import AgentState
from ..event_bus import get_event_bus, EventType, Event
from ..agent_memory import AgentMemory

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Abstract base class for all orchestration agents.
    Provides heartbeat, retry handling, structured logging, health checks,
    and graceful shutdown.
    """
    
    def __init__(self, name: str, session=None):
        self.name = name
        self.session = session
        self.bus = get_event_bus()
        self.memory = AgentMemory(name, session) if session else None
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        self.set_state(AgentState.IDLE)
        logger.info(f"[{self.name}] Initialized")

    def set_state(self, state: AgentState):
        if self.memory:
            self.memory.set_state(state)
        logger.debug(f"[{self.name}] State changed to {state}")

    def get_state(self) -> AgentState:
        return self.memory.get_state() if self.memory else AgentState.IDLE

    async def _heartbeat_loop(self):
        while self._running:
            # Emit heartbeat or update memory timestamp
            if self.memory:
                self.memory.update_last_active()
            await asyncio.sleep(10) # 10s heartbeat

    async def _process_loop(self):
        """Main loop to be overridden by subclasses if they do continuous work."""
        pass

    async def start(self):
        if self._running:
            return
        self._running = True
        self.set_state(AgentState.IDLE)
        self._task = asyncio.create_task(self._run_all())
        logger.info(f"[{self.name}] Started")

    async def _run_all(self):
        try:
            await asyncio.gather(
                self._heartbeat_loop(),
                self._process_loop()
            )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[{self.name}] Crashed: {e}", exc_info=True)
            self.set_state(AgentState.FAILED)
            await self.bus.publish(EventType.AGENT_FAILED, {"agent": self.name, "error": str(e)})

    async def stop(self):
        self._running = False
        self.set_state(AgentState.PAUSED)
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(f"[{self.name}] Stopped")

    async def handle_event(self, event: Event):
        """To be overridden by subclasses to handle specific events."""
        pass
