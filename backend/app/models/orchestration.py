from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from app.utils.uuid_utils import generate_uuid7

class AgentState(str, Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    GENERATING = "GENERATING"
    WAITING = "WAITING"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"

class ContentSchedule(SQLModel, table=True):
    __tablename__ = "content_schedule"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    platform: str = Field(index=True, nullable=False)
    publish_time: datetime = Field(nullable=False)
    priority: int = Field(default=0, nullable=False)
    trend_topic: str = Field(nullable=False)
    status: str = Field(default="PENDING", index=True, nullable=False)
    predicted_score: float = Field(default=0.0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class Campaign(SQLModel, table=True):
    __tablename__ = "campaign"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    name: str = Field(index=True, nullable=False)
    total_episodes: int = Field(default=20, nullable=False)
    current_episode: int = Field(default=0, nullable=False)
    storyline_persistence: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    recurring_characters: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class AgentMemoryRecord(SQLModel, table=True):
    __tablename__ = "agent_memory_record"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    agent_name: str = Field(index=True, nullable=False)
    state: str = Field(nullable=False)
    recent_decisions: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    recent_errors: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB, nullable=True))
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
