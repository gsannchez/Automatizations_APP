from sqlmodel import SQLModel, Field, Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from app.utils.uuid_utils import generate_uuid7

class ChannelProfile(SQLModel, table=True):
    __tablename__ = "channel_profile"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    name: str = Field(index=True, nullable=False)
    niche: str = Field(index=True, nullable=False)
    tone: str = Field(nullable=False)
    platform: str = Field(index=True, nullable=False)
    growth_score: float = Field(default=0.0)
    upload_frequency: str = Field(nullable=False)
    active: bool = Field(default=True)
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

class BrandIdentity(SQLModel, table=True):
    __tablename__ = "brand_identity"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    channel_id: UUID = Field(index=True, nullable=False)
    slogan: str = Field(nullable=True)
    visual_style: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    voice_profile: str = Field(nullable=False)
    target_audience: str = Field(nullable=False)
    consistency_score: float = Field(default=100.0)
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))

class NarrativeUniverse(SQLModel, table=True):
    __tablename__ = "narrative_universe"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    name: str = Field(index=True, nullable=False)
    universe_type: str = Field(nullable=False)
    continuity_rules: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    active_storylines: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))

class CharacterProfile(SQLModel, table=True):
    __tablename__ = "character_profile"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    universe_id: UUID = Field(index=True, nullable=False)
    name: str = Field(index=True, nullable=False)
    personality: str = Field(nullable=False)
    visual_traits: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    lore: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    emotional_profile: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))

class PublishingStrategy(SQLModel, table=True):
    __tablename__ = "publishing_strategy"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    channel_id: UUID = Field(index=True, nullable=False)
    preferred_times: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    target_platforms: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    pacing_profile: str = Field(nullable=False)
    hashtag_strategy: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    metadata_: Dict[str, Any] = Field(default_factory=dict, sa_column=Column("metadata", JSONB))
