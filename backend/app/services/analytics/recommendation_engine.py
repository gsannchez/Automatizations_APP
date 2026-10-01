"""Recommendation Engine — generates actionable recommendations for future content.

Analyzes historical ViralAnalysis + VideoPerformanceMetrics to recommend:
- Optimal styles
- Best performing hashtags
- Ideal video duration
- Content categories to pursue
"""
import logging
from typing import List, Dict, Optional, Any
from uuid import UUID

from sqlmodel import Session, select

from app.models.viral_intelligence import (
    VideoPerformanceMetrics,
    ViralAnalysis,
    TrendingTopic,
    ViralStyle,
)

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates content strategy recommendations using historical analytics.

    Combines trending topics, past viral scores, and performance metrics to
    suggest the highest-probability approach for the next video.
    """

    def __init__(self, session: Session):
        self.session = session

    def recommend_next_video(
        self,
        platform: str = "TIKTOK",
        category: Optional[str] = None,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """Generate comprehensive recommendations for the next video to create.

        Args:
            platform: Target platform (TIKTOK, INSTAGRAM, YOUTUBE).
            category: Optional content category filter.
            limit: Number of recommendations per category.

        Returns:
            Dict with style, hashtags, duration, hook templates, and category tips.
        """
        logger.info(f"Generating recommendations for {platform} | category={category}")

        # 1. Best performing styles from metrics
        best_style = self._recommend_best_style(platform)

        # 2. Top trending hashtags from DB
        trending_hashtags = self._get_top_hashtags(category, limit)

        # 3. Ideal duration based on avg watch time
        ideal_duration = self._recommend_duration(platform)

        # 4. Hook templates from top-performing trends
        hook_templates = self._get_hook_templates(category)

        # 5. Category recommendation
        top_category = self._get_top_category()

        return {
            "recommended_style": best_style,
            "trending_hashtags": trending_hashtags,
            "ideal_duration_seconds": ideal_duration,
            "hook_templates": hook_templates,
            "recommended_category": top_category,
            "platform": platform,
            "strategy_summary": self._build_strategy_summary(
                best_style, ideal_duration, top_category
            ),
        }

    def _recommend_best_style(self, platform: str) -> str:
        """Find the ViralStyle with highest avg views from historical data."""
        try:
            # Look at top viral analysis scores to infer style context
            top_analyses = self.session.exec(
                select(ViralAnalysis)
                .order_by(ViralAnalysis.overall_score.desc())  # type: ignore
                .limit(20)
            ).all()

            if not top_analyses:
                return ViralStyle.TIKTOK_NATIVE.value

            # For now heuristic: return most-used style from trend table
            trends = self.session.exec(select(TrendingTopic).limit(50)).all()
            style_counts: Dict[str, int] = {}
            for t in trends:
                style_counts[t.visual_style] = style_counts.get(t.visual_style, 0) + 1

            if style_counts:
                best = max(style_counts, key=lambda k: style_counts[k])
                return best

        except Exception as e:
            logger.warning(f"Style recommendation fallback: {e}")

        return ViralStyle.TIKTOK_NATIVE.value

    def _get_top_hashtags(
        self, category: Optional[str], limit: int
    ) -> List[str]:
        """Collect top hashtags from TrendingTopic table, filtered by category."""
        try:
            query = select(TrendingTopic).order_by(
                TrendingTopic.virality_score.desc()  # type: ignore
            ).limit(20)

            topics = self.session.exec(query).all()

            if category:
                topics = [t for t in topics if t.category.lower() == category.lower()]

            hashtags: List[str] = []
            for t in topics:
                if t.related_hashtags:
                    hashtags.extend(t.related_hashtags)

            # Deduplicate and limit
            seen = set()
            unique = []
            for h in hashtags:
                if h not in seen:
                    seen.add(h)
                    unique.append(h)
                if len(unique) >= limit:
                    break

            return unique if unique else ["#viral", "#fyp", "#foryou", "#trending", "#shorts"]

        except Exception as e:
            logger.warning(f"Hashtag recommendation fallback: {e}")
            return ["#viral", "#fyp", "#foryou", "#trending", "#shorts"]

    def _recommend_duration(self, platform: str) -> int:
        """Recommend optimal video duration in seconds based on platform and history."""
        try:
            metrics = self.session.exec(
                select(VideoPerformanceMetrics)
                .where(VideoPerformanceMetrics.platform == platform.upper())
                .limit(30)
            ).all()

            high_performers = [
                m for m in metrics
                if m.views > 1000 and m.average_watch_time > 0
            ]

            if high_performers:
                avg_watch = sum(m.average_watch_time for m in high_performers) / len(high_performers)
                # Optimal duration is slightly above avg watch time to avoid drop-off
                return min(int(avg_watch * 1.3), 90)

        except Exception as e:
            logger.warning(f"Duration recommendation fallback: {e}")

        # Platform defaults
        defaults = {"TIKTOK": 45, "INSTAGRAM": 30, "YOUTUBE": 60}
        return defaults.get(platform.upper(), 45)

    def _get_hook_templates(self, category: Optional[str]) -> List[str]:
        """Return hook templates from trending topics with highest virality scores."""
        try:
            topics = self.session.exec(
                select(TrendingTopic)
                .order_by(TrendingTopic.virality_score.desc())  # type: ignore
                .limit(10)
            ).all()

            templates: List[str] = []
            for t in topics:
                if t.hook_patterns:
                    templates.extend(t.hook_patterns)

            if templates:
                return list(dict.fromkeys(templates))[:5]  # deduplicated top 5

        except Exception as e:
            logger.warning(f"Hook template fallback: {e}")

        # Universal high-retention hooks (validated copywriting formulas)
        return [
            "Nadie esperaba lo que pasó después...",
            "Las cámaras captaron algo que no deberías ver.",
            "Hay una razón por la que esto está prohibido.",
            "Lo que encontraron cambió todo para siempre.",
            "El secreto que [X] no quiere que sepas.",
        ]

    def _get_top_category(self) -> str:
        """Find the category with highest average virality score."""
        try:
            topics = self.session.exec(select(TrendingTopic).limit(100)).all()
            if not topics:
                return "horror"

            category_scores: Dict[str, List[float]] = {}
            for t in topics:
                category_scores.setdefault(t.category, []).append(t.virality_score)

            best_cat = max(
                category_scores,
                key=lambda c: sum(category_scores[c]) / len(category_scores[c]),
            )
            return best_cat

        except Exception as e:
            logger.warning(f"Category recommendation fallback: {e}")
            return "horror"

    def _build_strategy_summary(
        self, style: str, duration: int, category: str
    ) -> str:
        """Build a human-readable strategy summary."""
        return (
            f"Para maximizar la retención en tu próximo vídeo, "
            f"usa el estilo '{style}' con una duración de {duration}s "
            f"enfocado en la categoría '{category}'. "
            f"Asegúrate de usar un gancho narrativo en los primeros 3 segundos "
            f"y mantén el pacing por encima de 2.5 palabras por segundo."
        )
