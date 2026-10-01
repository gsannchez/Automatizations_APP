"""
app/services/creative_feedback/performance_feedback_loop.py

Phase 10: Master coordinator for the creative feedback loop. Takes in real-world 
analytics and updates the Cinematic Memory and Strategy Engine.
"""
import logging
from typing import Dict, Any

from .feedback_modules import StrategyEvolution, RetentionLearning, ViralPatternLearning
from ..cinematic_memory.memory_manager import CinematicMemoryManager

logger = logging.getLogger(__name__)

class PerformanceFeedbackLoop:
    def __init__(self, memory_manager: CinematicMemoryManager):
        self.memory = memory_manager
        self.evolution = StrategyEvolution()
        self.retention = RetentionLearning()
        self.viral = ViralPatternLearning()

    def process_analytics_webhook(self, job_id: str, platform: str, analytics_data: Dict[str, Any]):
        """
        Ingests real-world performance metrics (e.g., from TikTok/YouTube APIs)
        and adjusts the AI Director's future decisions.
        """
        logger.info(f"[PerformanceFeedbackLoop] Processing analytics for {job_id}")
        
        ctr = analytics_data.get("ctr", 0)
        completion_rate = analytics_data.get("completion_rate", 0)
        
        # Calculate a blended performance score
        performance_score = (ctr * 0.4) + (completion_rate * 0.6)
        
        # Log to memory (using mock scenes for signature extraction)
        mock_scenes = [{"prompt": "mock"}] 
        self.memory.record_job_outcome(mock_scenes, performance_score, analytics_data.get("tenant_id", "default"))
        
        # Learn from drops
        drops = self.retention.analyze_retention_drop(analytics_data)
        if "drop_at_3s" in drops:
            logger.warning(f"[PerformanceFeedbackLoop] Weak hook detected for {job_id}.")
            
        logger.info(f"[PerformanceFeedbackLoop] Feedback loop complete. Score: {performance_score}")
