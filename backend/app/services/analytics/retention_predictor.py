"""Retention Predictor — predicts future video retention using historical data.

Uses lightweight statistical analysis on VideoPerformanceMetrics.
No heavy ML framework required — pure math with numpy fallback.
"""
import logging
import math
from typing import List, Dict, Optional, Any
from uuid import UUID

from sqlmodel import Session, select

from app.models.viral_intelligence import VideoPerformanceMetrics, ViralAnalysis

logger = logging.getLogger(__name__)


class RetentionPredictor:
    """Predicts expected retention and performance for new videos.

    Uses historical VideoPerformanceMetrics + ViralAnalysis scores to derive
    a performance prediction via weighted heuristic regression.
    No cloud inference. No GPU required. Pure local statistics.
    """

    def __init__(self, session: Session):
        self.session = session

    def predict_performance(
        self,
        viral_score: float,
        hook_strength: float,
        pacing_score: float,
        platform: str = "TIKTOK",
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Predict expected performance for a new video given its viral analysis scores.

        Args:
            viral_score: Overall viral score (0-100).
            hook_strength: Hook strength (0.0-1.0).
            pacing_score: Pacing score (0.0-1.0).
            platform: Target platform for prediction context.
            category: Optional content category for filtered comparison.

        Returns:
            Dict with predicted_views_tier, predicted_retention, confidence.
        """
        # Fetch historical baselines from DB
        historical = self._get_historical_baselines(platform, category)

        # Heuristic model: linear regression weights tuned for short-form content
        base_retention = 0.30  # Default baseline 30% for vertical short-form
        retention_boost = (
            hook_strength * 0.25
            + pacing_score * 0.15
            + (viral_score / 100.0) * 0.20
        )

        if historical:
            # Adjust with empirical historical average
            hist_avg_retention = sum(
                m["avg_watch_time"] / max(m["duration_estimate"], 1.0)
                for m in historical
            ) / len(historical)
            hist_avg_retention = min(hist_avg_retention, 1.0)
            base_retention = (base_retention * 0.4) + (hist_avg_retention * 0.6)

        predicted_retention = min(base_retention + retention_boost, 1.0)
        predicted_retention = round(predicted_retention * 100.0, 1)

        # Tier classification based on predicted retention %
        views_tier = self._classify_views_tier(predicted_retention, viral_score)

        # Confidence based on sample size
        confidence = self._compute_confidence(len(historical))

        logger.info(
            f"Retention prediction: {predicted_retention}% | "
            f"tier={views_tier} | confidence={confidence}"
        )

        return {
            "predicted_retention_pct": predicted_retention,
            "views_tier": views_tier,
            "confidence": confidence,
            "historical_samples": len(historical),
            "platform": platform,
            "notes": self._generate_prediction_notes(
                predicted_retention, hook_strength, pacing_score
            ),
        }

    def _get_historical_baselines(
        self, platform: str, category: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Fetch recent performance metrics from DB for regression baseline."""
        try:
            metrics = self.session.exec(
                select(VideoPerformanceMetrics)
                .where(VideoPerformanceMetrics.platform == platform.upper())
                .limit(50)
            ).all()

            results = []
            for m in metrics:
                if m.views > 0:
                    results.append({
                        "avg_watch_time": m.average_watch_time,
                        "duration_estimate": 60.0,  # Default 60s short-form
                        "views": m.views,
                        "likes": m.likes,
                        "ctr": m.ctr,
                    })
            return results
        except Exception as e:
            logger.warning(f"Could not fetch historical baselines: {e}")
            return []

    def _classify_views_tier(self, retention_pct: float, viral_score: float) -> str:
        """Classify expected view range based on retention and viral score."""
        combined = (retention_pct * 0.6) + (viral_score * 0.4)
        if combined >= 70:
            return "VIRAL (100k–1M+)"
        elif combined >= 55:
            return "HIGH (10k–100k)"
        elif combined >= 40:
            return "MEDIUM (1k–10k)"
        elif combined >= 25:
            return "LOW (100–1k)"
        else:
            return "MINIMAL (<100)"

    def _compute_confidence(self, sample_size: int) -> str:
        """Return a confidence label based on historical sample count."""
        if sample_size >= 30:
            return "HIGH"
        elif sample_size >= 10:
            return "MEDIUM"
        elif sample_size >= 3:
            return "LOW"
        else:
            return "SPECULATIVE (no data)"

    def _generate_prediction_notes(
        self, retention_pct: float, hook_strength: float, pacing_score: float
    ) -> List[str]:
        """Generate natural-language prediction notes for the user."""
        notes = []
        if retention_pct >= 65:
            notes.append("✅ Alta retención prevista — el contenido tiene potencial viral real.")
        elif retention_pct >= 40:
            notes.append("⚠️ Retención media — optimizar el gancho puede aumentar el alcance significativamente.")
        else:
            notes.append("❌ Baja retención prevista — revisar estructura narrativa completa antes de generar.")

        if hook_strength < 0.5:
            notes.append("🔴 El gancho débil es el principal factor limitante de retención.")
        if pacing_score < 0.5:
            notes.append("🔴 El pacing lento reduce la expectativa de retención en un ~15%.")
        return notes
