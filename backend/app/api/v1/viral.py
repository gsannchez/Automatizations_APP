"""Viral Score API — /api/v1/viral-score/

Endpoints for scoring scripts, improving hooks, and storing ViralAnalysis records.
"""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from app.core.database import get_sync_session
from app.models.viral_intelligence import ViralAnalysis
from app.services.viral.viral_scorer import ViralScorer
from app.services.story.narrative_engine import NarrativeEngine

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Viral Score"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class ScoreScriptRequest(BaseModel):
    script_text: str = Field(..., min_length=20, description="Script to analyze.")
    scene_durations: List[float] = Field(
        default=[10.0],
        description="Duration in seconds for each scene.",
    )
    video_id: Optional[UUID] = Field(
        None,
        description="Optional: link this analysis to an existing video.",
    )
    improve_hook: bool = Field(
        True,
        description="If true, also returns an AI-improved version of the script hook.",
    )


class ViralScoreResponse(BaseModel):
    analysis_id: UUID
    hook_strength: float
    retention_probability: float
    pacing_score: float
    emotional_intensity: float
    curiosity_gap: float
    trend_alignment: float
    overall_score: float
    recommendations: Optional[List[str]]
    improved_script: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisListItem(BaseModel):
    id: UUID
    overall_score: float
    hook_strength: float
    created_at: str

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/score",
    response_model=ViralScoreResponse,
    summary="Score a script for viral potential",
    description=(
        "Analyzes a video script for hook strength, retention probability, pacing, "
        "emotional intensity, curiosity gap, and trend alignment. "
        "Optionally rewrites the hook for maximum impact."
    ),
)
async def score_script(
    body: ScoreScriptRequest,
    session: Session = Depends(get_sync_session),
):
    """Score a script and return detailed ViralAnalysis with recommendations."""
    try:
        scorer = ViralScorer(session=session)
        analysis = scorer.analyze_script(
            script_text=body.script_text,
            scene_durations=body.scene_durations,
            video_id=body.video_id,
        )

        improved = None
        if body.improve_hook:
            try:
                narrative = NarrativeEngine()
                result = narrative.optimize_script(body.script_text)
                improved = result.get("optimized_script")
            except Exception as e:
                logger.warning(f"Hook improvement failed (non-critical): {e}")

        return ViralScoreResponse(
            analysis_id=analysis.id,
            hook_strength=analysis.hook_strength,
            retention_probability=analysis.retention_probability,
            pacing_score=analysis.pacing_score,
            emotional_intensity=analysis.emotional_intensity,
            curiosity_gap=analysis.curiosity_gap,
            trend_alignment=analysis.trend_alignment,
            overall_score=analysis.overall_score,
            recommendations=analysis.recommendations,
            improved_script=improved,
        )
    except Exception as e:
        logger.error(f"Viral scoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.get(
    "/history",
    response_model=List[ViralScoreResponse],
    summary="List past viral analyses",
)
async def list_analyses(
    video_id: Optional[UUID] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_sync_session),
):
    """Return historical viral analyses, optionally filtered by video_id."""
    query = select(ViralAnalysis).order_by(ViralAnalysis.created_at.desc()).limit(limit)  # type: ignore
    analyses = session.exec(query).all()

    if video_id:
        analyses = [a for a in analyses if a.video_id == video_id]

    return [
        ViralScoreResponse(
            analysis_id=a.id,
            hook_strength=a.hook_strength,
            retention_probability=a.retention_probability,
            pacing_score=a.pacing_score,
            emotional_intensity=a.emotional_intensity,
            curiosity_gap=a.curiosity_gap,
            trend_alignment=a.trend_alignment,
            overall_score=a.overall_score,
            recommendations=a.recommendations,
        )
        for a in analyses
    ]


@router.get(
    "/{analysis_id}",
    response_model=ViralScoreResponse,
    summary="Get a specific viral analysis by ID",
)
async def get_analysis(
    analysis_id: UUID,
    session: Session = Depends(get_sync_session),
):
    """Retrieve one ViralAnalysis record by UUID."""
    analysis = session.get(ViralAnalysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Viral analysis not found.")

    return ViralScoreResponse(
        analysis_id=analysis.id,
        hook_strength=analysis.hook_strength,
        retention_probability=analysis.retention_probability,
        pacing_score=analysis.pacing_score,
        emotional_intensity=analysis.emotional_intensity,
        curiosity_gap=analysis.curiosity_gap,
        trend_alignment=analysis.trend_alignment,
        overall_score=analysis.overall_score,
        recommendations=analysis.recommendations,
    )
