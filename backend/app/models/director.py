from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from app.utils.uuid_utils import generate_uuid7

class SceneQualityReport(SQLModel, table=True):
    __tablename__ = "scene_quality_report"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    tenant_id: str = Field(index=True, nullable=False, default="default")
    job_id: str = Field(index=True, nullable=False)
    scene_id: str = Field(index=True, nullable=False)
    quality_score: str = Field(nullable=False) # CRITICAL, LOW, ACCEPTABLE, GOOD, EXCELLENT
    metrics: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    failure_reasons: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    regeneration_recommended: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class NarrativeAnalysis(SQLModel, table=True):
    __tablename__ = "narrative_analysis"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    tenant_id: str = Field(index=True, nullable=False, default="default")
    job_id: str = Field(index=True, nullable=False)
    narrative_score: float = Field(nullable=False)
    retention_prediction: float = Field(nullable=False)
    pacing_alerts: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    emotional_graph: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class RegenerationAttempt(SQLModel, table=True):
    __tablename__ = "regeneration_attempt"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    tenant_id: str = Field(index=True, nullable=False, default="default")
    job_id: str = Field(index=True, nullable=False)
    scene_id: str = Field(index=True, nullable=False)
    attempt_number: int = Field(nullable=False, default=1)
    prompt_mutations: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    fallback_strategy_used: str = Field(nullable=True)
    success: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class VariantBattle(SQLModel, table=True):
    __tablename__ = "variant_battle"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    tenant_id: str = Field(index=True, nullable=False, default="default")
    job_id: str = Field(index=True, nullable=False)
    battle_type: str = Field(nullable=False) # hook, pacing, thumbnail
    variants: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    winner_id: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class VisualConsistencyReport(SQLModel, table=True):
    __tablename__ = "visual_consistency_report"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    tenant_id: str = Field(index=True, nullable=False, default="default")
    job_id: str = Field(index=True, nullable=False)
    continuity_score: float = Field(nullable=False)
    visual_drift_alerts: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class CinematicPattern(SQLModel, table=True):
    __tablename__ = "cinematic_pattern"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    tenant_id: str = Field(index=True, nullable=False, default="default")
    pattern_type: str = Field(nullable=False, index=True) # success, failure
    pattern_signature: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    performance_score: float = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
