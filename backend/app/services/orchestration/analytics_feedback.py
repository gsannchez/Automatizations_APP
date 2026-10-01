"""Phase 8: Advanced Analytics Feedback — closes the learning loop."""
import logging
from datetime import datetime
from typing import Any, Dict, List

from sqlmodel import Session, select

from ...models.viral_intelligence import VideoPerformanceMetrics, HookTemplate, StylePerformance

logger = logging.getLogger(__name__)

WINNING_CTR_THRESHOLD = 0.06       # 6% CTR = winning
WINNING_RETENTION_THRESHOLD = 0.55  # 55% avg watch = winning
FAILING_CTR_THRESHOLD = 0.02


class AnalyticsFeedback:
    """
    Reads real VideoPerformanceMetrics and updates hook/style scores in the DB.
    Feeds updated signals back to DecisionEngine and TrendRanker.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def run_feedback_cycle(self) -> Dict[str, Any]:
        metrics = self.session.exec(
            select(VideoPerformanceMetrics)
            .order_by(VideoPerformanceMetrics.updated_at.desc())
            .limit(200)
        ).all()

        if not metrics:
            return {"status": "no_data", "processed": 0}

        winning_styles: Dict[str, List[float]] = {}
        failing_styles: Dict[str, List[float]] = {}
        hook_boosts: Dict[str, float] = {}

        for m in metrics:
            ctr = m.ctr
            retention = m.average_watch_time / 60.0 if m.average_watch_time else 0.0
            score = (ctr * 100) * 0.5 + retention * 50.0

            platform = m.platform or "TIKTOK"

            if ctr >= WINNING_CTR_THRESHOLD and retention >= WINNING_RETENTION_THRESHOLD:
                winning_styles.setdefault(platform, []).append(score)
            elif ctr <= FAILING_CTR_THRESHOLD:
                failing_styles.setdefault(platform, []).append(score)

        # Update StylePerformance records
        updated = 0
        for platform, scores in winning_styles.items():
            avg = sum(scores) / len(scores)
            existing = self.session.exec(
                select(StylePerformance)
                .where(StylePerformance.platform == platform)
                .order_by(StylePerformance.score.desc())
            ).first()
            if existing:
                existing.score = round((existing.score + avg) / 2, 2)
                existing.usage_count += 1
                existing.last_used = datetime.utcnow()
                self.session.add(existing)
                updated += 1

        self.session.commit()
        logger.info(f"[AnalyticsFeedback] Feedback cycle complete. Metrics processed: {len(metrics)}, records updated: {updated}")

        return {
            "status": "ok",
            "processed": len(metrics),
            "winning_platforms": list(winning_styles.keys()),
            "failing_platforms": list(failing_styles.keys()),
            "style_records_updated": updated,
        }

    def get_top_styles(self, limit: int = 10) -> List[Dict[str, Any]]:
        styles = self.session.exec(
            select(StylePerformance).order_by(StylePerformance.score.desc()).limit(limit)
        ).all()
        return [
            {
                "style_name": s.style_name,
                "platform": s.platform,
                "score": s.score,
                "usage_count": s.usage_count,
                "success_rate": s.success_rate,
            }
            for s in styles
        ]
