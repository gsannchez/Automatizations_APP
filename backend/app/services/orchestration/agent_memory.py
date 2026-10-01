"""Phase 8: Agent Memory System — persists each agent's state to PostgreSQL."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ...models.orchestration import AgentMemoryRecord, AgentState
from ...utils.uuid_utils import generate_uuid7

logger = logging.getLogger(__name__)


class AgentMemory:
    """
    Manages persistent memory for a named agent.
    All decisions and errors are serialised into JSONB.
    """

    def __init__(self, agent_name: str, session: Session) -> None:
        self.agent_name = agent_name
        self.session = session

    def _load(self) -> AgentMemoryRecord:
        record = self.session.exec(
            select(AgentMemoryRecord).where(AgentMemoryRecord.agent_name == self.agent_name)
        ).first()
        if not record:
            record = AgentMemoryRecord(
                agent_name=self.agent_name,
                state=AgentState.IDLE.value,
                recent_decisions={},
                recent_errors=[],
            )
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        return record

    def get_state(self) -> AgentState:
        record = self._load()
        try:
            return AgentState(record.state)
        except ValueError:
            return AgentState.IDLE

    def set_state(self, state: AgentState) -> None:
        record = self._load()
        record.state = state.value
        record.updated_at = datetime.utcnow()
        self.session.add(record)
        self.session.commit()
        logger.info(f"[AgentMemory] {self.agent_name} -> {state.value}")

    def record_decision(self, key: str, value: Any) -> None:
        record = self._load()
        decisions = record.recent_decisions or {}
        decisions[key] = {"value": value, "ts": datetime.utcnow().isoformat()}
        # Keep only last 50 decisions
        if len(decisions) > 50:
            oldest = sorted(decisions.keys())[0]
            del decisions[oldest]
        record.recent_decisions = decisions
        record.updated_at = datetime.utcnow()
        self.session.add(record)
        self.session.commit()

    def record_error(self, error: str) -> None:
        record = self._load()
        errors: List[str] = record.recent_errors or []
        errors.append(f"{datetime.utcnow().isoformat()}: {error}")
        record.recent_errors = errors[-20:]  # retain last 20
        record.updated_at = datetime.utcnow()
        self.session.add(record)
        self.session.commit()

    def snapshot(self) -> Dict[str, Any]:
        record = self._load()
        return {
            "agent": self.agent_name,
            "state": record.state,
            "recent_decisions": record.recent_decisions,
            "recent_errors": record.recent_errors,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }
