import random
from ...models.viral_intelligence import TrendingTopic
from .trend_combiner import TrendCombiner
from .content_variator import ContentVariator
from ..trends_engine.format_mapper import FormatMapper

class IdeaGenerator:
    """Autonomous content creation based on trends."""

    @staticmethod
    def generate(trend: TrendingTopic) -> dict:
        """
        Takes a top trend as input and generates a structured video idea.
        """
        format_type = trend.format_type or FormatMapper.map_format(trend.topic)
        emotions = ["shocking", "heartwarming", "suspenseful", "informative"]
        emotion = random.choice(emotions)

        combined = TrendCombiner.combine(trend.topic, format_type, emotion)
        variants = ContentVariator.generate_variants(combined)
        
        # Pick one variant randomly
        selected = random.choice(variants)

        # Simple heuristic hook generator (will be optimized later by HookOptimizer)
        hooks = [
            f"You won't believe what happened in this {trend.topic}...",
            f"This is the craziest {trend.topic} I've ever seen.",
            f"Watch until the end of this {trend.topic}!",
            f"Why is nobody talking about this {trend.topic}?"
        ]

        return {
            "idea": selected["idea"],
            "hook": random.choice(hooks),
            "style": format_type,
            "emotion": emotion,
            "duration": selected["duration"]
        }
