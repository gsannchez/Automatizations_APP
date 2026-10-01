import logging
from typing import List
from datetime import datetime
from sqlmodel import Session, select
from ...models.viral_intelligence import TrendingTopic

logger = logging.getLogger(__name__)

class TrendCollector:
    """Simulates ingestion of trending topics from social media."""
    
    def __init__(self, session: Session):
        self.session = session
        # Simple in-memory cache to prevent duplicate processing
        self._cache = set()

    def collect_synthetic_trends(self) -> List[TrendingTopic]:
        """Generates synthetic trends and stores them in PostgreSQL."""
        synthetic_data = [
            {
                "topic": "dog rescue",
                "category": "animals",
                "velocity_score": 85.5,
                "reuse_count": 1200,
                "engagement_rate": 0.15,
                "format_type": "BODYCAM",
            },
            {
                "topic": "crime footage",
                "category": "news",
                "velocity_score": 92.0,
                "reuse_count": 3400,
                "engagement_rate": 0.22,
                "format_type": "CCTV",
            },
            {
                "topic": "movie recap",
                "category": "entertainment",
                "velocity_score": 78.3,
                "reuse_count": 850,
                "engagement_rate": 0.11,
                "format_type": "CINEMATIC",
            },
            {
                "topic": "reddit story",
                "category": "storytime",
                "velocity_score": 88.9,
                "reuse_count": 5000,
                "engagement_rate": 0.18,
                "format_type": "STORYTIME",
            }
        ]
        
        new_trends = []
        try:
            for data in synthetic_data:
                topic_name = data["topic"]
                if topic_name in self._cache:
                    continue
                
                # Check DB to prevent duplicates
                existing = self.session.execute(
                    select(TrendingTopic).where(TrendingTopic.topic == topic_name)
                ).scalars().first()
                
                if existing:
                    # Update existing
                    existing.velocity_score = data["velocity_score"]
                    existing.reuse_count = data["reuse_count"]
                    existing.engagement_rate = data["engagement_rate"]
                    existing.format_type = data["format_type"]
                    existing.last_seen = datetime.utcnow()
                    self.session.add(existing)
                    new_trends.append(existing)
                else:
                    # Create new
                    new_trend = TrendingTopic(
                        topic=topic_name,
                        category=data["category"],
                        velocity_score=data["velocity_score"],
                        reuse_count=data["reuse_count"],
                        engagement_rate=data["engagement_rate"],
                        format_type=data["format_type"],
                        last_seen=datetime.utcnow()
                    )
                    self.session.add(new_trend)
                    new_trends.append(new_trend)
                
                self._cache.add(topic_name)
                
            self.session.commit()
            for t in new_trends:
                self.session.refresh(t)
            logger.info(f"Collected {len(new_trends)} synthetic trends.")
            return new_trends
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error collecting trends: {e}")
            raise
