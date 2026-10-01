"""
app/services/ai_director/render_supervisor.py

Phase 10: Coordinates with the Scene Quality Engine to grade a render.
Saves the report to the database.
"""
import logging
from sqlmodel import Session
from app.models.director import SceneQualityReport

# We will implement this in Step 2, but we need the interface now
from ..quality_ai.scene_quality_analyzer import SceneQualityAnalyzer

logger = logging.getLogger(__name__)

class RenderSupervisor:
    def __init__(self, session: Session):
        self.session = session
        self.analyzer = SceneQualityAnalyzer()

    async def analyze_scene(self, job_id: str, scene_id: str, video_path: str, tenant_id: str) -> SceneQualityReport:
        """
        Runs the video through the Quality AI and persists the report.
        """
        # 1. Analyze
        quality_result = await self.analyzer.evaluate_video(video_path)
        
        # 2. Persist
        report = SceneQualityReport(
            tenant_id=tenant_id,
            job_id=job_id,
            scene_id=scene_id,
            quality_score=quality_result["score"],
            metrics=quality_result["metrics"],
            failure_reasons=quality_result["failure_reasons"],
            regeneration_recommended=quality_result["regeneration_recommended"]
        )
        
        self.session.add(report)
        self.session.commit()
        
        logger.info(f"[RenderSupervisor] Report saved for {scene_id}: Score={report.quality_score}")
        
        return report
