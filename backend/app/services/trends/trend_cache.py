"""Local caching service for social trends."""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TrendCache:
    """Handles JSON file-based local caching for active social trends."""
    
    def __init__(self, cache_file: str = "media/trends_cache.json", ttl_hours: int = 12):
        self.cache_file = cache_file
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        
    def get_cached_trends(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve trends from cache if cache exists and is not expired."""
        if not os.path.exists(self.cache_file):
            return None
            
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            timestamp_str = data.get("timestamp")
            if not timestamp_str:
                return None
                
            timestamp = datetime.fromisoformat(timestamp_str)
            if datetime.utcnow() - timestamp > self.ttl:
                logger.info("Trend cache expired.")
                return None
                
            logger.info("Retrieved trends from local cache successfully.")
            return data.get("trends")
        except Exception as e:
            logger.error(f"Error reading trend cache: {str(e)}")
            return None
            
    def set_cached_trends(self, trends: List[Dict[str, Any]]) -> None:
        """Save trends into local cache file with current timestamp."""
        try:
            data = {
                "timestamp": datetime.utcnow().isoformat(),
                "trends": trends
            }
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(trends)} trending topics to local cache file.")
        except Exception as e:
            logger.error(f"Error saving trend cache: {str(e)}")
