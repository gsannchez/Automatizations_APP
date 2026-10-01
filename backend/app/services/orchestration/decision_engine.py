"""Phase 8: Autonomous Decision Engine — global content prioritization."""
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .resource_planner import ResourcePlanner, SystemHealth

logger = logging.getLogger(__name__)


@dataclass
class DecisionPlan:
    content_priority: str       # "urgent" | "normal" | "low"
    render_tier: str            # "high" | "medium" | "low"
    platform: str
    style: str
    ai_video_allowed: bool
    estimated_roi: float        # 0.0 - 100.0
    rationale: str


class DecisionEngine:
    """
    Takes inputs from trends, analytics, system health, and historical performance
    and outputs a DecisionPlan that drives the generation loop.
    """

    def __init__(self) -> None:
        self.planner = ResourcePlanner()

    def evaluate(
        self,
        top_trend_score: float = 0.0,
        retention_history_avg: float = 0.0,
        saturation_ratio: float = 0.0,
        platform_hint: Optional[str] = None,
        style_hint: Optional[str] = None,
    ) -> DecisionPlan:

        health = self.planner.evaluate()

        # --- Content Priority ---
        if top_trend_score > 80 and saturation_ratio < 0.3:
            priority = "urgent"
        elif top_trend_score > 50:
            priority = "normal"
        else:
            priority = "low"

        # --- Platform selection ---
        platform = platform_hint or "TIKTOK"

        # --- Style selection ---
        style = style_hint or "TIKTOK_NATIVE"

        # --- ROI estimate ---
        base_roi = top_trend_score * 0.6 + retention_history_avg * 0.4
        roi_penalty = saturation_ratio * 30.0
        estimated_roi = max(0.0, min(100.0, base_roi - roi_penalty))

        rationale = (
            f"trend_score={top_trend_score:.1f} saturation={saturation_ratio:.2f} "
            f"retention_avg={retention_history_avg:.1f} health={health.render_tier}"
        )

        plan = DecisionPlan(
            content_priority=priority,
            render_tier=health.render_tier,
            platform=platform,
            style=style,
            ai_video_allowed=health.ai_video_allowed,
            estimated_roi=estimated_roi,
            rationale=rationale,
        )
        logger.info(f"[DecisionEngine] Plan: priority={priority} roi={estimated_roi:.1f} tier={health.render_tier}")
        return plan

    def to_dict(self, plan: DecisionPlan) -> Dict[str, Any]:
        return {
            "content_priority": plan.content_priority,
            "render_tier": plan.render_tier,
            "platform": plan.platform,
            "style": plan.style,
            "ai_video_allowed": plan.ai_video_allowed,
            "estimated_roi": round(plan.estimated_roi, 2),
            "rationale": plan.rationale,
        }
