"""Viral Scorer orchestrator service."""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlmodel import Session, select

from app.models.viral_intelligence import ViralAnalysis, TrendingTopic
from .hook_analyzer import HookAnalyzer
from .retention_estimator import RetentionEstimator
from .pacing_analyzer import PacingAnalyzer
from .emotional_intensity import EmotionalIntensity

logger = logging.getLogger(__name__)

class ViralScorer:
    """Orchestrates comprehensive script scoring, recommendation engine, and DB persistence."""
    
    def __init__(self, session: Session):
        self.session = session
        self.hook_analyzer = HookAnalyzer()
        self.retention_estimator = RetentionEstimator()
        self.pacing_analyzer = PacingAnalyzer()
        self.emotional_intensity = EmotionalIntensity()
        
    def analyze_script(self, script_text: str, scene_durations: List[float], video_id: Optional[UUID] = None) -> ViralAnalysis:
        """Run deep viral analytics on voiceover and scene timings.
        
        Args:
            script_text: Voiceover text to analyze.
            scene_durations: List of seconds per scene.
            video_id: Optional UUID relation to GeneratedVideo.
            
        Returns:
            ViralAnalysis SQLModel object.
        """
        logger.info("Starting viral script scoring engine...")
        
        # 1. Component evaluations
        hook_res = self.hook_analyzer.analyze_hook(script_text)
        hook_score = hook_res["hook_score"]
        
        ret_res = self.retention_estimator.estimate_retention(hook_score, script_text, scene_durations)
        ret_score = ret_res["average_retention"]
        
        pace_res = self.pacing_analyzer.analyze_pacing(script_text, scene_durations)
        pace_score = pace_res["pacing_score"]
        
        emo_res = self.emotional_intensity.analyze_emotions(script_text)
        intensity_score = emo_res["emotional_intensity"]
        gap_score = emo_res["curiosity_gap"]
        
        # 2. Trend alignment check
        # Scan TrendingTopic table in DB for matching words/hashtags
        trends = self.session.exec(select(TrendingTopic)).all()
        trend_alignment = 0.15 # Default baseline
        
        matched_trends = []
        for trend in trends:
            # Check if trend topic word is contained inside script
            words = trend.topic.lower().split()
            matched_words = [w for w in words if w in script_text.lower() and len(w) > 3]
            if len(matched_words) >= 2 or trend.category.lower() in script_text.lower():
                matched_trends.append(trend.topic)
                trend_alignment += 0.25
                
        trend_alignment = min(trend_alignment, 1.0)
        
        # 3. Overall composite score (0 to 100)
        # Hook strength and emotional curiosity gap are heavily weighted for TikTok/Shorts
        composite = (
            (hook_score * 0.30) +
            (ret_score * 0.25) +
            (pace_score * 0.15) +
            (intensity_score * 0.10) +
            (gap_score * 0.10) +
            (trend_alignment * 0.10)
        )
        overall_score = round(composite * 100.0, 1)
        
        # 4. Generate recommendations
        recs = []
        if hook_score < 0.5:
            recs.append("El gancho es débil. Usa fórmulas de tensión como 'Las cámaras grabaron esto' en las primeras 5 palabras.")
        if pace_score < 0.6:
            recs.append(f"Optimiza el pacing. El WPS actual es de {pace_res['wps']} (objetivo: 2.2 a 3.2 palabras por segundo).")
        if intensity_score < 0.4:
            recs.append("Aumenta la carga dramática. Introduce palabras clave emocionales como 'secreto', 'prohibido' o 'impactante'.")
        if gap_score < 0.5:
            recs.append("Inserta brechas de curiosidad: haz una afirmación intrigante al inicio y no des el desenlace de inmediato.")
        if trend_alignment < 0.4:
            recs.append("Alinea mejor el contenido con las tendencias activas en base de datos agregando palabras clave del sector.")
            
        if not recs:
            recs.append("¡Excelente guion! El análisis viral no ha detectado fallos importantes. Listo para generar.")
            
        # 5. Persist to database
        analysis = ViralAnalysis(
            video_id=video_id,
            script_text=script_text,
            hook_strength=hook_score,
            retention_probability=ret_score,
            pacing_score=pace_score,
            emotional_intensity=intensity_score,
            curiosity_gap=gap_score,
            trend_alignment=trend_alignment,
            overall_score=overall_score,
            recommendations=recs
        )
        
        self.session.add(analysis)
        self.session.commit()
        self.session.refresh(analysis)
        
        return analysis
