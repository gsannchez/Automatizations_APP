"""
app/api/v1/director.py

Phase 10: API endpoints for the Autonomous AI Director to expose quality reports, 
narrative scoring, variant battles, and regeneration history.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, Any, List

from app.core.database import get_sync_session
from app.models.director import (
    SceneQualityReport, 
    NarrativeAnalysis, 
    RegenerationAttempt,
    VariantBattle,
    VisualConsistencyReport
)

router = APIRouter(prefix="/director", tags=["Director"])

@router.get("/status/{job_id}", response_model=Dict[str, Any])
def get_director_status(job_id: str, session: Session = Depends(get_sync_session)):
    """Aggregate status of all director evaluations for a specific job."""
    quality = session.exec(select(SceneQualityReport).where(SceneQualityReport.job_id == job_id)).all()
    narrative = session.exec(select(NarrativeAnalysis).where(NarrativeAnalysis.job_id == job_id)).first()
    regen = session.exec(select(RegenerationAttempt).where(RegenerationAttempt.job_id == job_id)).all()
    
    return {
        "job_id": job_id,
        "quality_evaluations": len(quality),
        "narrative_score": narrative.narrative_score if narrative else None,
        "regeneration_attempts": len(regen),
        "status": "healthy"
    }

@router.get("/quality/{job_id}", response_model=List[SceneQualityReport])
def get_quality_reports(job_id: str, session: Session = Depends(get_sync_session)):
    reports = session.exec(select(SceneQualityReport).where(SceneQualityReport.job_id == job_id)).all()
    return reports

@router.get("/narrative/{job_id}", response_model=NarrativeAnalysis)
def get_narrative_analysis(job_id: str, session: Session = Depends(get_sync_session)):
    analysis = session.exec(select(NarrativeAnalysis).where(NarrativeAnalysis.job_id == job_id)).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Narrative analysis not found")
    return analysis

@router.get("/variants/{job_id}", response_model=List[VariantBattle])
def get_variant_battles(job_id: str, session: Session = Depends(get_sync_session)):
    battles = session.exec(select(VariantBattle).where(VariantBattle.job_id == job_id)).all()
    return battles

@router.get("/regeneration/{job_id}", response_model=List[RegenerationAttempt])
def get_regeneration_history(job_id: str, session: Session = Depends(get_sync_session)):
    attempts = session.exec(select(RegenerationAttempt).where(RegenerationAttempt.job_id == job_id)).all()
    return attempts

@router.get("/consistency/{job_id}", response_model=VisualConsistencyReport)
def get_consistency_report(job_id: str, session: Session = Depends(get_sync_session)):
    report = session.exec(select(VisualConsistencyReport).where(VisualConsistencyReport.job_id == job_id)).first()
    if not report:
        raise HTTPException(status_code=404, detail="Consistency report not found")
    return report
