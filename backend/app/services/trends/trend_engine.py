"""Orchestrator for Trend Engine module."""
import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select

from app.models.viral_intelligence import TrendingTopic
from .tiktok_scraper import TikTokScraper
from .trend_scorer import TrendScorer
from .trend_analyzer import TrendAnalyzer
from .trend_cache import TrendCache

logger = logging.getLogger(__name__)

class TrendEngine:
    """Orchestrates social trend discovery, scoring, styling, and persistence."""
    
    def __init__(self, session: Session):
        self.session = session
        self.scraper = TikTokScraper()
        self.scorer = TrendScorer()
        self.analyzer = TrendAnalyzer()
        self.cache = TrendCache()
        
    def refresh_and_get_trends(self, force: bool = False) -> List[TrendingTopic]:
        """Orchestrate trend refresh, updating database and cache, and return TrendingTopic list.
        
        Args:
            force: Skip cache lookup and force live scraping.
            
        Returns:
            List of TrendingTopic SQLModel objects.
        """
        logger.info("Executing TrendEngine orchestration...")
        
        # 1. Try cache if not forced
        if not force:
            cached_data = self.cache.get_cached_trends()
            if cached_data:
                # Resolve from DB using cached topics names or return DB records
                existing_topics = self.session.exec(select(TrendingTopic)).all()
                if existing_topics:
                    return list(existing_topics)
                    
        # 2. Fetch fresh trend signals from scraper
        raw_signals = self.scraper.fetch_public_trends()
        processed_topics: List[TrendingTopic] = []
        
        # 3. Process, score and persist
        for raw in raw_signals:
            topic_name = raw.get("topic", "")
            
            # Check if topic already exists in DB
            stmt = select(TrendingTopic).where(TrendingTopic.topic == topic_name)
            topic_record = self.session.exec(stmt).first()
            
            # Scores & Styles calculation
            scores = self.scorer.calculate_metrics(raw)
            styles = self.analyzer.analyze_patterns(raw)
            
            if not topic_record:
                # Create new
                topic_record = TrendingTopic(
                    topic=topic_name,
                    category=raw.get("category", "tiktok_native"),
                    virality_score=scores["virality_score"],
                    momentum_score=scores["momentum_score"],
                    engagement_rate=scores["engagement_rate"],
                    hook_patterns=styles["hook_patterns"],
                    related_hashtags=styles["related_hashtags"],
                    pacing_style=styles["pacing_style"],
                    visual_style=styles["visual_style"]
                )
            else:
                # Update existing
                topic_record.virality_score = scores["virality_score"]
                topic_record.momentum_score = scores["momentum_score"]
                topic_record.engagement_rate = scores["engagement_rate"]
                topic_record.hook_patterns = styles["hook_patterns"]
                topic_record.related_hashtags = styles["related_hashtags"]
                topic_record.pacing_style = styles["pacing_style"]
                topic_record.visual_style = styles["visual_style"]
                topic_record.updated_at = datetime.utcnow()
                
            self.session.add(topic_record)
            processed_topics.append(topic_record)
            
        self.session.commit()
        
        # 4. Update cache
        cacheable_list = [
            {
                "topic": t.topic,
                "category": t.category,
                "virality_score": t.virality_score,
                "momentum_score": t.momentum_score,
                "engagement_rate": t.engagement_rate,
                "hook_patterns": t.hook_patterns,
                "related_hashtags": t.related_hashtags,
                "pacing_style": t.pacing_style,
                "visual_style": t.visual_style
            }
            for t in processed_topics
        ]
        self.cache.set_cached_trends(cacheable_list)
        
        return processed_topics
