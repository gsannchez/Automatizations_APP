"""Analyzer service to extract stylistic, narrative, and hook patterns from trends."""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Extracts styles, typical pacing, associated hashtags, and hook patterns from social signals."""
    
    def analyze_patterns(self, raw_trend: Dict[str, Any]) -> Dict[str, Any]:
        """Examine hashtags and topic description to deduce visual style, pacing, and viral hook formulas.
        
        Args:
            raw_trend: Raw dictionary from scraper.
            
        Returns:
            Dict containing hook_patterns, related_hashtags, pacing_style, and visual_style.
        """
        category = raw_trend.get("category", "tiktok_native").lower()
        topic = raw_trend.get("topic", "")
        
        # 1. Pacing & Visual Style deduction based on topic category
        pacing_style = raw_trend.get("pacing", "medium")
        visual_style = raw_trend.get("visual_style", "tiktok_native")
        
        # 2. Extract hook templates
        hooks = raw_trend.get("hooks", [])
        if not hooks:
            hooks = [
                f"La verdad sobre {topic} que nadie te contará...",
                f"Esto es lo que pasó realmente en {topic}...",
                f"Si te gusta {category}, tienes que ver esto..."
            ]
            
        # 3. Assemble and return
        return {
            "hook_patterns": hooks,
            "related_hashtags": raw_trend.get("hashtags", ["viral", "trending", category]),
            "pacing_style": pacing_style,
            "visual_style": visual_style
        }
