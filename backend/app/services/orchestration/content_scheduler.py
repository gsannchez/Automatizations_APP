"""Phase 8: Content Scheduler — autonomous generation queue manager."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select

from ...models.orchestration import ContentSchedule
from ...utils.uuid_utils import generate_uuid7
from .decision_engine import DecisionEngine

logger = logging.getLogger(__name__)


# Best posting windows per platform (hour of day, UTC)
OPTIMAL_HOURS: Dict[str, List[int]] = {
    "TIKTOK": [7, 12, 18, 21],
    "INSTAGRAM_REELS": [8, 13, 17, 20],
    "YOUTUBE_SHORTS": [9, 15, 19],
}


class ContentScheduler:
    """
    Plans and queues content generation slots.
    Avoids trend saturation and balances platform output.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self.engine = DecisionEngine()

    def _next_optimal_slot(self, platform: str) -> datetime:
        """Find the next optimal UTC hour for publishing on the given platform."""
        hours = OPTIMAL_HOURS.get(platform.upper(), [12, 18])
        now = datetime.utcnow()
        for h in sorted(hours):
            candidate = now.replace(hour=h, minute=0, second=0, microsecond=0)
            if candidate > now:
                return candidate
        # All hours passed today — schedule for first slot tomorrow
        return (now + timedelta(days=1)).replace(hour=hours[0], minute=0, second=0, microsecond=0)

    def schedule_item(
        self,
        trend_topic: str,
        platform: str,
        top_trend_score: float = 50.0,
        saturation_ratio: float = 0.0,
    ) -> ContentSchedule:
        plan = self.engine.evaluate(
            top_trend_score=top_trend_score,
            saturation_ratio=saturation_ratio,
            platform_hint=platform,
        )
        slot = self._next_optimal_slot(platform)
        schedule = ContentSchedule(
            platform=platform,
            publish_time=slot,
            priority={"urgent": 10, "normal": 5, "low": 1}.get(plan.content_priority, 5),
            trend_topic=trend_topic,
            status="PENDING",
            predicted_score=plan.estimated_roi,
        )
        self.session.add(schedule)
        self.session.commit()
        self.session.refresh(schedule)
        logger.info(f"[ContentScheduler] Scheduled '{trend_topic}' on {platform} @ {slot.isoformat()} | priority={plan.content_priority}")
        return schedule

    def get_pending(self, limit: int = 10) -> List[ContentSchedule]:
        return self.session.exec(
            select(ContentSchedule)
            .where(ContentSchedule.status == "PENDING")
            .order_by(ContentSchedule.priority.desc(), ContentSchedule.publish_time.asc())
            .limit(limit)
        ).all()

    def mark_running(self, schedule_id) -> None:
        item = self.session.get(ContentSchedule, schedule_id)
        if item:
            item.status = "RUNNING"
            self.session.add(item)
            self.session.commit()

    def mark_done(self, schedule_id) -> None:
        item = self.session.get(ContentSchedule, schedule_id)
        if item:
            item.status = "DONE"
            self.session.add(item)
            self.session.commit()

    def list_all(self, limit: int = 50) -> List[Dict[str, Any]]:
        items = self.session.exec(
            select(ContentSchedule)
            .order_by(ContentSchedule.priority.desc())
            .limit(limit)
        ).all()
        return [
            {
                "id": str(i.id),
                "platform": i.platform,
                "publish_time": i.publish_time.isoformat(),
                "priority": i.priority,
                "trend_topic": i.trend_topic,
                "status": i.status,
                "predicted_score": i.predicted_score,
            }
            for i in items
        ]
