"""Trends API — /api/v1/trends/

Endpoints for TrendingTopic management and automated trend refresh.
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_sync_session
from app.models.viral_intelligence import TrendingTopic
from app.services.trends.trend_engine import TrendEngine
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Trends"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class TrendingTopicResponse(BaseModel):
    id: UUID
    topic: str
    category: str
    virality_score: float
    momentum_score: float
    engagement_rate: float
    hook_patterns: Optional[List[str]]
    related_hashtags: Optional[List[str]]
    pacing_style: str
    visual_style: str

    class Config:
        from_attributes = True


class TrendRefreshResponse(BaseModel):
    status: str
    message: str
    topics_found: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=List[TrendingTopicResponse],
    summary="List all trending topics",
    description="Returns all trending topics stored in the database, ordered by virality score descending.",
)
async def list_trends(
    category: Optional[str] = Query(None, description="Filter by category (e.g. horror, news, cctv)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    session: Session = Depends(get_sync_session),
):
    """Return all trending topics, optionally filtered by category."""
    query = select(TrendingTopic).order_by(TrendingTopic.virality_score.desc()).limit(limit)  # type: ignore
    topics = session.exec(query).all()

    if category:
        topics = [t for t in topics if t.category.lower() == category.lower()]

    return topics


@router.get(
    "/{topic_id}",
    response_model=TrendingTopicResponse,
    summary="Get a single trending topic by ID",
)
async def get_trend(
    topic_id: UUID,
    session: Session = Depends(get_sync_session),
):
    """Retrieve a specific trending topic by its UUID."""
    topic = session.get(TrendingTopic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Trending topic not found.")
    return topic


@router.post(
    "/refresh",
    response_model=TrendRefreshResponse,
    summary="Trigger automated trend refresh",
    description="Runs the TrendEngine pipeline in the background to fetch and persist new trending topics.",
)
async def refresh_trends(
    background_tasks: BackgroundTasks,
    category: Optional[str] = Query(None, description="Optional category to focus on"),
    session: Session = Depends(get_sync_session),
):
    """Trigger background trend refresh via TrendEngine."""

    def _run_refresh():
        try:
            engine = TrendEngine(session=session)
            results = engine.run(category_filter=category)
            logger.info(f"TrendEngine refresh complete: {len(results)} topics stored.")
        except Exception as e:
            logger.error(f"TrendEngine refresh failed: {e}", exc_info=True)

    background_tasks.add_task(_run_refresh)

    return TrendRefreshResponse(
        status="queued",
        message="Trend refresh initiated in background. Check /api/v1/trends/ in a few seconds.",
        topics_found=0,
    )


@router.delete(
    "/{topic_id}",
    summary="Delete a trending topic",
    status_code=204,
)
async def delete_trend(
    topic_id: UUID,
    session: Session = Depends(get_sync_session),
):
    """Remove a trending topic from the database."""
    topic = session.get(TrendingTopic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Trending topic not found.")
    session.delete(topic)
    session.commit()
