"""
app/services/cinematic_memory/memory_manager.py

Phase 10: Coordinates the storage and retrieval of cinematic patterns to 
inform the Creative Decision Engine.
"""
import logging
from typing import Dict, Any, List
from sqlmodel import Session

from .memory_modules import (
    SuccessfulPatterns,
    FailedPatterns,
    StyleMemory,
    CinematicEmbeddings,
    VisualSignature
)

logger = logging.getLogger(__name__)

class CinematicMemoryManager:
    def __init__(self, session: Session):
        self.session = session
        self.success = SuccessfulPatterns(session)
        self.failure = FailedPatterns(session)
        self.style = StyleMemory()
        self.embeddings = CinematicEmbeddings()
        self.signature = VisualSignature()

    def record_job_outcome(self, scenes: List[Dict[str, Any]], performance_score: float, tenant_id: str):
        """
        Called after a video finishes its lifecycle and gets a final performance score.
        """
        logger.info(f"[CinematicMemory] Recording outcome. Score: {performance_score}")
        
        sig = self.signature.extract(scenes)
        
        if performance_score > 85.0:
            self.success.record(sig, performance_score, tenant_id)
        elif performance_score < 40.0:
            self.failure.record(sig, performance_score, tenant_id)
            
        self.session.commit()

    def get_style_recommendation(self, tenant_id: str, platform: str) -> str:
        """
        Provides a data-backed style recommendation for a new generation.
        """
        return self.style.recall_best_style(tenant_id, platform)
