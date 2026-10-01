"""Models for Phase 4: Viral Intelligence Engine."""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum
from app.utils.uuid_utils import generate_uuid7


class ViralStyle(str, Enum):
    CCTV = "cctv"
    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"
    NEWS = "news"
    TIKTOK_NATIVE = "tiktok_native"
    HORROR = "horror"
    MEME_REALISM = "meme_realism"
    BODYCAM = "bodycam"
    DASHCAM = "dashcam"
    ANIME_EDIT = "anime_edit"
    CINEMATIC_AI = "cinematic_ai"


class TrendingTopic(SQLModel, table=True):
    """Trending topics automatically extracted from TikTok/social media feeds.
    
    Attributes:
        id: UUID v7 primary key
        topic: Main trending topic or search term
        category: Niche/category (e.g. horror, news, CCTV)
        virality_score: Normalized virality score (0.0 to 100.0)
        momentum_score: Speed of trend adoption (0.0 to 100.0)
        engagement_rate: Average engagement rate (likes/views) of the trend
        hook_patterns: List of hook structures identified in viral videos
        related_hashtags: List of hashtags associated with this trend
        pacing_style: Expected pacing style (e.g. fast, steady, dramatic)
        visual_style: Expected visual style mapping to ViralStyle
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "trending_topic"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    topic: str = Field(index=True, nullable=False)
    category: str = Field(index=True, nullable=False)
    virality_score: float = Field(default=0.0, nullable=False)
    momentum_score: float = Field(default=0.0, nullable=False)
    engagement_rate: float = Field(default=0.0, nullable=False)
    velocity_score: float = Field(default=0.0, nullable=False)
    reuse_count: int = Field(default=0, nullable=False)
    format_type: Optional[str] = Field(default=None, nullable=True)
    last_seen: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    hook_patterns: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    related_hashtags: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    pacing_style: str = Field(default="medium", nullable=False)
    visual_style: str = Field(default="tiktok_native", nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )


class ViralAnalysis(SQLModel, table=True):
    """Viral scoring and retention analysis of a script or generated video.
    
    Attributes:
        id: UUID v7 primary key
        video_id: Foreign key to GeneratedVideo (optional if script only)
        script_text: Raw script content analyzed
        hook_strength: Estimated strength of the hook in the first 3s (0.0 - 1.0)
        retention_probability: Estimated average retention probability (0.0 - 1.0)
        pacing_score: Score representing rhythm and pacing optimization (0.0 - 1.0)
        emotional_intensity: Estimated average emotional response (0.0 - 1.0)
        curiosity_gap: Level of suspense and curiosity gap (0.0 - 1.0)
        trend_alignment: Level of alignment with active trends (0.0 - 1.0)
        overall_score: Overall calculated viral score (0.0 - 100.0)
        recommendations: Actionable bullet points to improve script
        created_at: Creation timestamp
    """
    __tablename__ = "viral_analysis"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    video_id: Optional[UUID] = Field(
        default=None,
        foreign_key="video.id",
        index=True,
        nullable=True
    )
    script_text: str = Field(sa_column=Column(Text, nullable=False))
    hook_strength: float = Field(default=0.0, nullable=False)
    retention_probability: float = Field(default=0.0, nullable=False)
    pacing_score: float = Field(default=0.0, nullable=False)
    emotional_intensity: float = Field(default=0.0, nullable=False)
    curiosity_gap: float = Field(default=0.0, nullable=False)
    trend_alignment: float = Field(default=0.0, nullable=False)
    overall_score: float = Field(default=0.0, nullable=False)
    recommendations: Optional[List[str]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        nullable=False
    )


class ContentEmbedding(SQLModel, table=True):
    """Vector database index simulator for local FAISS and sentence-transformers.
    
    Stores high-dimensional embeddings for generated scenes, assets, and styles.
    
    Attributes:
        id: UUID v7 primary key
        entity_id: UUID of the related object (e.g. video_id, asset_id, scene_idx)
        entity_type: Type of entity (e.g. 'scene_text', 'video_asset', 'audio_asset')
        vector_data: High-dimensional float array storing the embedding
        metadata: Key-value metadata dictionary for context filtering
        created_at: Creation timestamp
    """
    __tablename__ = "content_embedding"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    entity_id: UUID = Field(index=True, nullable=False)
    entity_type: str = Field(index=True, nullable=False)
    vector_data: List[float] = Field(sa_column=Column(JSONB, nullable=False))
    extra_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        nullable=False
    )


class ClipAnalysis(SQLModel, table=True):
    """Automated scene highlights and clips extracted from long movies/series.
    
    Attributes:
        id: UUID v7 primary key
        source_video_path: Absolute or relative path to the original long video
        clip_path: Path to the generated vertical 9:16 highlight video segment
        start_time: Start time in seconds relative to original video
        end_time: End time in seconds relative to original video
        highlight_score: Estimated highlight score (0.0 to 1.0)
        transcript: Subtitle transcription of the clip segment
        emotional_tone: Dominant emotional tone of the scene (e.g. tension, humor, anger)
        created_at: Creation timestamp
    """
    __tablename__ = "clip_analysis"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    source_video_path: str = Field(nullable=False)
    clip_path: str = Field(nullable=False)
    start_time: float = Field(nullable=False)
    end_time: float = Field(nullable=False)
    highlight_score: float = Field(default=0.0, nullable=False)
    transcript: str = Field(sa_column=Column(Text, nullable=False))
    emotional_tone: str = Field(default="neutral", nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        index=True,
        nullable=False
    )


class VideoPerformanceMetrics(SQLModel, table=True):
    """Social media performance metrics for video feedback loop.
    
    Attributes:
        id: UUID v7 primary key
        video_id: Foreign key to GeneratedVideo
        views: View count
        likes: Like count
        shares: Share count
        comments: Comment count
        average_watch_time: Average watch time in seconds
        retention_data: Watch-time retention curves as a map of {time: percentage}
        ctr: Click-through rate (0.0 to 1.0)
        platform: Target social platform (TIKTOK, INSTAGRAM, YOUTUBE)
        updated_at: Last update timestamp
    """
    __tablename__ = "video_performance_metrics"
    
    id: UUID = Field(
        default_factory=generate_uuid7,
        primary_key=True,
        nullable=False
    )
    video_id: UUID = Field(
        foreign_key="video.id",
        index=True,
        nullable=False
    )
    views: int = Field(default=0, nullable=False)
    likes: int = Field(default=0, nullable=False)
    shares: int = Field(default=0, nullable=False)
    comments: int = Field(default=0, nullable=False)
    average_watch_time: float = Field(default=0.0, nullable=False)
    retention_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )
    ctr: float = Field(default=0.0, nullable=False)
    platform: str = Field(nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

class ViralPattern(SQLModel, table=True):
    """Persists successful narrative structures or ideas."""
    __tablename__ = "viral_pattern"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    pattern_type: str = Field(index=True, nullable=False) # e.g. 'narrative', 'pacing'
    pattern_data: str = Field(nullable=False)
    score: float = Field(default=0.0, nullable=False)
    usage_count: int = Field(default=0, nullable=False)
    success_rate: float = Field(default=0.0, nullable=False)
    last_used: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class HookTemplate(SQLModel, table=True):
    """Stores successful hook structures."""
    __tablename__ = "hook_template"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    template_text: str = Field(nullable=False)
    emotion: str = Field(nullable=False)
    score: float = Field(default=0.0, nullable=False)
    usage_count: int = Field(default=0, nullable=False)
    success_rate: float = Field(default=0.0, nullable=False)
    last_used: datetime = Field(default_factory=datetime.utcnow, nullable=False)

class StylePerformance(SQLModel, table=True):
    """Tracks performance of visual styles across platforms."""
    __tablename__ = "style_performance"
    id: UUID = Field(default_factory=generate_uuid7, primary_key=True)
    style_name: str = Field(index=True, nullable=False)
    platform: str = Field(index=True, nullable=False)
    score: float = Field(default=0.0, nullable=False)
    usage_count: int = Field(default=0, nullable=False)
    success_rate: float = Field(default=0.0, nullable=False)
    last_used: datetime = Field(default_factory=datetime.utcnow, nullable=False)
