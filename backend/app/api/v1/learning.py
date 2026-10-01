from fastapi import APIRouter, Depends
from sqlmodel import Session
from ...core.database import get_sync_session
from ...services.autonomous_learning.performance_feedback import PerformanceFeedbackEngine
from ...services.autonomous_learning.trend_saturation import TrendSaturationDetector

router = APIRouter(tags=["Autonomous Learning"])

@router.get("/insights")
def get_insights(session: Session = Depends(get_sync_session)):
    engine = PerformanceFeedbackEngine(session)
    return engine.analyze_history()

@router.get("/saturation")
def get_saturation():
    # Placeholder for aggregate saturation stats
    return {"status": "ok", "message": "Trend saturation stats not fully implemented in DB."}

@router.get("/top-hooks")
def get_top_hooks(session: Session = Depends(get_sync_session)):
    engine = PerformanceFeedbackEngine(session)
    insights = engine.analyze_history()
    return {"top_hooks": insights.winning_hooks}

@router.get("/platform-stats")
def get_platform_stats():
    return {"status": "ok", "message": "Platform stats tracking active."}
