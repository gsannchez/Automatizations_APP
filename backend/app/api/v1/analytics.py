"""Analytics API — /api/v1/analytics/ and /api/v1/recommendations/

Endpoints for performance tracking, engagement analysis, retention prediction,
and next-video content strategy recommendations.
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from app.core.database import get_sync_session
from app.models.viral_intelligence import VideoPerformanceMetrics
from app.services.analytics.performance_tracker import PerformanceTracker
from app.services.analytics.engagement_analyzer import EngagementAnalyzer
from app.services.analytics.retention_predictor import RetentionPredictor
from app.services.analytics.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analytics"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RecordMetricsRequest(BaseModel):
    video_id: UUID
    platform: str = Field(..., example="TIKTOK")
    views: int = Field(0, ge=0)
    likes: int = Field(0, ge=0)
    shares: int = Field(0, ge=0)
    comments: int = Field(0, ge=0)
    average_watch_time: float = Field(0.0, ge=0.0)
    ctr: float = Field(0.0, ge=0.0, le=1.0)
    retention_data: Optional[dict] = Field(
        None,
        description="Map of time_seconds (str) → retention_percentage (float). E.g. {'0': 100, '5': 85, '10': 70}",
    )


class MetricsResponse(BaseModel):
    id: UUID
    video_id: UUID
    platform: str
    views: int
    likes: int
    shares: int
    comments: int
    average_watch_time: float
    ctr: float
    engagement_rate: float

    class Config:
        from_attributes = True


class RetentionAnalysisRequest(BaseModel):
    retention_data: dict = Field(
        ...,
        description="Map of time_seconds → retention_percentage.",
        example={"0": 100, "5": 88, "10": 72, "20": 55, "30": 40, "45": 25},
    )
    video_duration: float = Field(..., description="Total video duration in seconds.")


class PredictionRequest(BaseModel):
    viral_score: float = Field(..., ge=0.0, le=100.0)
    hook_strength: float = Field(..., ge=0.0, le=1.0)
    pacing_score: float = Field(..., ge=0.0, le=1.0)
    platform: str = Field(default="TIKTOK")
    category: Optional[str] = None


class RecommendationRequest(BaseModel):
    platform: str = Field(default="TIKTOK")
    category: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/metrics",
    response_model=MetricsResponse,
    summary="Record or update performance metrics for a video",
    description="Stores social platform metrics (views, likes, CTR, retention curve) for a generated video.",
)
async def record_metrics(
    body: RecordMetricsRequest,
    session: Session = Depends(get_sync_session),
):
    """Create or update VideoPerformanceMetrics for a given video + platform."""
    tracker = PerformanceTracker(session=session)
    metrics = tracker.record_metrics(
        video_id=body.video_id,
        platform=body.platform,
        views=body.views,
        likes=body.likes,
        shares=body.shares,
        comments=body.comments,
        average_watch_time=body.average_watch_time,
        ctr=body.ctr,
        retention_data=body.retention_data,
    )
    engagement_rate = tracker.compute_engagement_rate(metrics)

    return MetricsResponse(
        id=metrics.id,
        video_id=metrics.video_id,
        platform=metrics.platform,
        views=metrics.views,
        likes=metrics.likes,
        shares=metrics.shares,
        comments=metrics.comments,
        average_watch_time=metrics.average_watch_time,
        ctr=metrics.ctr,
        engagement_rate=engagement_rate,
    )


@router.get(
    "/metrics/{video_id}",
    response_model=List[MetricsResponse],
    summary="Get performance metrics for a video",
)
async def get_metrics(
    video_id: UUID,
    platform: Optional[str] = Query(None),
    session: Session = Depends(get_sync_session),
):
    """Retrieve all metrics records for a video, optionally filtered by platform."""
    tracker = PerformanceTracker(session=session)
    metrics_list = tracker.get_metrics(video_id=video_id, platform=platform)

    return [
        MetricsResponse(
            id=m.id,
            video_id=m.video_id,
            platform=m.platform,
            views=m.views,
            likes=m.likes,
            shares=m.shares,
            comments=m.comments,
            average_watch_time=m.average_watch_time,
            ctr=m.ctr,
            engagement_rate=tracker.compute_engagement_rate(m),
        )
        for m in metrics_list
    ]


@router.post(
    "/retention-analysis",
    summary="Analyze a retention curve for drop-off patterns",
    description=(
        "Takes a time→retention% map and returns engagement grade, "
        "drop-off events, peak moments and per-scene recommendations."
    ),
)
async def analyze_retention(body: RetentionAnalysisRequest):
    """Analyze a retention curve and return engagement insights."""
    analyzer = EngagementAnalyzer()
    result = analyzer.analyze_retention_curve(
        retention_data={str(k): float(v) for k, v in body.retention_data.items()},
        video_duration=body.video_duration,
    )
    return result


@router.post(
    "/predict",
    summary="Predict performance tier for a video before generation",
    description=(
        "Uses viral analysis scores to predict expected retention %, "
        "views tier (VIRAL/HIGH/MEDIUM/LOW), and confidence level."
    ),
)
async def predict_performance(
    body: PredictionRequest,
    session: Session = Depends(get_sync_session),
):
    """Predict video performance based on viral analysis scores."""
    predictor = RetentionPredictor(session=session)
    return predictor.predict_performance(
        viral_score=body.viral_score,
        hook_strength=body.hook_strength,
        pacing_score=body.pacing_score,
        platform=body.platform,
        category=body.category,
    )


@router.post(
    "/recommendations",
    summary="Get content strategy recommendations for the next video",
    description=(
        "Analyzes historical performance data and active trends to recommend "
        "the optimal style, hashtags, duration, hooks, and category for your next video."
    ),
)
async def get_recommendations(
    body: RecommendationRequest,
    session: Session = Depends(get_sync_session),
):
    """Generate next-video content strategy recommendations."""
    engine = RecommendationEngine(session=session)
    return engine.recommend_next_video(
        platform=body.platform,
        category=body.category,
        limit=body.limit,
    )


@router.get(
    "/recommendations",
    summary="Quick recommendations with GET (default TIKTOK)",
)
async def get_recommendations_quick(
    platform: str = Query("TIKTOK"),
    category: Optional[str] = Query(None),
    session: Session = Depends(get_sync_session),
):
    """Quick GET-based recommendations endpoint."""
    engine = RecommendationEngine(session=session)
    return engine.recommend_next_video(platform=platform, category=category)
