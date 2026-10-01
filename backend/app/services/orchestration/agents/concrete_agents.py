import logging
import asyncio
from typing import Optional
from sqlmodel import Session

from .base_agent import BaseAgent
from ...models.orchestration import AgentState
from ..event_bus import EventType, Event

logger = logging.getLogger(__name__)

class TrendAgent(BaseAgent):
    """
    Agent responsible for monitoring and discovering trends.
    """
    def __init__(self, session: Optional[Session] = None):
        super().__init__("TrendAgent", session)
        
    async def _process_loop(self):
        while self._running:
            self.set_state(AgentState.THINKING)
            logger.info("[TrendAgent] Searching for trends...")
            await asyncio.sleep(2) # Mock trend search
            
            # Emit trend discovered event
            await self.bus.publish(EventType.TREND_DETECTED, {
                "trend": "Mock Trend 1",
                "score": 85.0
            })
            
            self.set_state(AgentState.WAITING)
            await asyncio.sleep(60) # Wait before searching again
            
class IdeaAgent(BaseAgent):
    def __init__(self, session: Optional[Session] = None):
        super().__init__("IdeaAgent", session)
        self.bus.subscribe(EventType.TREND_DETECTED, self.handle_event)
        
    async def handle_event(self, event: Event):
        if event.event_type == EventType.TREND_DETECTED:
            self.set_state(AgentState.EXECUTING)
            logger.info(f"[IdeaAgent] Generating idea for trend: {event.payload.get('trend')}")
            await asyncio.sleep(1) # Mock idea generation
            # Suppose it emits IDEA_GENERATED, but for now we just log
            self.set_state(AgentState.IDLE)

class ScriptAgent(BaseAgent):
    def __init__(self, session: Optional[Session] = None):
        super().__init__("ScriptAgent", session)

class RenderAgent(BaseAgent):
    def __init__(self, session: Optional[Session] = None):
        super().__init__("RenderAgent", session)

class UploadAgent(BaseAgent):
    def __init__(self, session: Optional[Session] = None):
        super().__init__("UploadAgent", session)

class AnalyticsAgent(BaseAgent):
    def __init__(self, session: Optional[Session] = None):
        super().__init__("AnalyticsAgent", session)

class LearningAgent(BaseAgent):
    def __init__(self, session: Optional[Session] = None):
        super().__init__("LearningAgent", session)
