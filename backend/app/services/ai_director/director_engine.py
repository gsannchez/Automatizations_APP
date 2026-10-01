"""
app/services/ai_director/director_engine.py

Phase 10: The core AI Director that oversees the entire generation
lifecycle. Coordinates scene pre-checks, quality analysis, and regeneration.
"""
import logging
from typing import Dict, Any, List

from app.models.director import SceneQualityReport, RegenerationAttempt
from sqlmodel import Session
from .scene_supervisor import SceneSupervisor
from .render_supervisor import RenderSupervisor
from .creative_decision_engine import CreativeDecisionEngine

logger = logging.getLogger(__name__)

class DirectorEngine:
    def __init__(self, session: Session):
        self.session = session
        self.scene_supervisor = SceneSupervisor()
        self.render_supervisor = RenderSupervisor(session)
        self.creative_decision = CreativeDecisionEngine()

    async def precheck_script(self, script_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Runs before generation starts to validate script structure, pacing, and constraints."""
        logger.info(f"[DirectorEngine] Running precheck for platform {platform}")
        
        # Validate deterministic rules (duration, transitions)
        warnings = self.scene_supervisor.validate_script(script_data, platform)
        
        # Make creative adjustments if needed
        adjusted_script = self.creative_decision.optimize_script(script_data, warnings)
        
        return {
            "status": "approved" if not warnings else "adjusted",
            "warnings": warnings,
            "script": adjusted_script
        }

    async def evaluate_render(self, job_id: str, scene_id: str, video_path: str, tenant_id: str) -> SceneQualityReport:
        """Runs after a scene is rendered to score quality and decide on regeneration."""
        logger.info(f"[DirectorEngine] Evaluating render {scene_id} for job {job_id}")
        
        report = await self.render_supervisor.analyze_scene(
            job_id=job_id,
            scene_id=scene_id,
            video_path=video_path,
            tenant_id=tenant_id
        )
        
        if report.regeneration_recommended:
            logger.warning(f"[DirectorEngine] Scene {scene_id} failed quality checks. Triggering regeneration.")
            
        return report

    async def plan_regeneration(self, report: SceneQualityReport, original_prompt: str) -> RegenerationAttempt:
        """Decides how to mutate the prompt or settings based on the failure reason."""
        logger.info(f"[DirectorEngine] Planning regeneration for {report.scene_id}")
        
        mutation = self.creative_decision.mutate_for_regeneration(
            original_prompt, 
            report.failure_reasons
        )
        
        attempt = RegenerationAttempt(
            tenant_id=report.tenant_id,
            job_id=report.job_id,
            scene_id=report.scene_id,
            prompt_mutations=mutation,
            fallback_strategy_used=mutation.get("strategy", "unknown")
        )
        self.session.add(attempt)
        self.session.commit()
        
        return attempt
