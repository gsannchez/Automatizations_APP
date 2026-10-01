"""Performance Tracker — records and updates social media metrics for videos.

Architecture is ready for TikTok/Instagram/YouTube API integration.
Currently stores manually-ingested data or placeholder values.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session, select

from app.models.viral_intelligence import VideoPerformanceMetrics

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Stores and updates social platform performance metrics per video.

    Designed for future integration with TikTok Business API, Instagram Graph
    API, and YouTube Data API v3. Currently operates in manual/stub mode.
    """

    def __init__(self, session: Session):
        self.session = session

    def record_metrics(
        self,
        video_id: UUID,
        platform: str,
        views: int = 0,
        likes: int = 0,
        shares: int = 0,
        comments: int = 0,
        average_watch_time: float = 0.0,
        ctr: float = 0.0,
        retention_data: Optional[Dict[str, Any]] = None,
    ) -> VideoPerformanceMetrics:
        """Create or update performance metrics for a video.

        Args:
            video_id: UUID of the GeneratedVideo.
            platform: Social platform name (e.g. 'TIKTOK', 'INSTAGRAM', 'YOUTUBE').
            views: Total view count.
            likes: Total like count.
            shares: Share count.
            comments: Comment count.
            average_watch_time: Average watch time in seconds.
            ctr: Click-through rate (0.0 to 1.0).
            retention_data: Optional dict mapping seconds to retention percentage.

        Returns:
            Created or updated VideoPerformanceMetrics instance.
        """
        # Check if a record already exists for this video + platform
        existing = self.session.exec(
            select(VideoPerformanceMetrics).where(
                VideoPerformanceMetrics.video_id == video_id,
                VideoPerformanceMetrics.platform == platform.upper(),
            )
        ).first()

        if existing:
            logger.info(
                f"Updating metrics for video {video_id} on {platform}."
            )
            existing.views = views
            existing.likes = likes
            existing.shares = shares
            existing.comments = comments
            existing.average_watch_time = average_watch_time
            existing.ctr = ctr
            existing.retention_data = retention_data
            existing.updated_at = datetime.utcnow()
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing

        logger.info(
            f"Recording new metrics for video {video_id} on {platform}."
        )
        metrics = VideoPerformanceMetrics(
            video_id=video_id,
            platform=platform.upper(),
            views=views,
            likes=likes,
            shares=shares,
            comments=comments,
            average_watch_time=average_watch_time,
            ctr=ctr,
            retention_data=retention_data,
        )
        self.session.add(metrics)
        self.session.commit()
        self.session.refresh(metrics)
        return metrics

    def get_metrics(
        self, video_id: UUID, platform: Optional[str] = None
    ) -> list[VideoPerformanceMetrics]:
        """Retrieve all recorded metrics for a video, optionally filtered by platform.

        Args:
            video_id: UUID of the GeneratedVideo.
            platform: Optional platform filter.

        Returns:
            List of VideoPerformanceMetrics records.
        """
        query = select(VideoPerformanceMetrics).where(
            VideoPerformanceMetrics.video_id == video_id
        )
        if platform:
            query = query.where(
                VideoPerformanceMetrics.platform == platform.upper()
            )
        return list(self.session.exec(query).all())

    def compute_engagement_rate(self, metrics: VideoPerformanceMetrics) -> float:
        """Compute standard engagement rate: (likes + comments + shares) / views.

        Args:
            metrics: A VideoPerformanceMetrics instance.

        Returns:
            Engagement rate as a float between 0.0 and 1.0.
        """
        if metrics.views == 0:
            return 0.0
        interactions = metrics.likes + metrics.comments + metrics.shares
        return round(interactions / metrics.views, 4)
