class TrendCombiner:
    """Combines a trend, format, and emotion into a base core idea."""
    
    @staticmethod
    def combine(trend_topic: str, format_type: str, emotional_tone: str) -> dict:
        """Outputs a structured base idea."""
        return {
            "topic": trend_topic,
            "format": format_type,
            "emotion": emotional_tone,
            "core_idea": f"A {emotional_tone} {format_type} video about {trend_topic}"
        }
