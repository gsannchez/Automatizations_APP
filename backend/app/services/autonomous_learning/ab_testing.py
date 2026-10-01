from dataclasses import dataclass
import random
from .hook_evolution import HookEvolution

@dataclass
class ABVariantSet:
    hook_a: str
    hook_b: str
    title_a: str
    title_b: str
    cta_a: str
    cta_b: str

class ABTestingEngine:
    """Generates A/B variants for a single video."""
    
    CTAS = [
        "Follow for more!",
        "Like and subscribe!",
        "What do you think? Comment below!",
        "Share this with a friend!"
    ]
    
    @classmethod
    def generate_variants(cls, base_idea: dict) -> ABVariantSet:
        hook_a = base_idea.get("hook", "Wait until the end!")
        hook_b = HookEvolution.evolve(hook_a, base_idea)
        
        topic = base_idea.get("topic", "Video")
        
        return ABVariantSet(
            hook_a=hook_a,
            hook_b=hook_b,
            title_a=f"The Truth About {topic}",
            title_b=f"{topic} Explained",
            cta_a=random.choice(cls.CTAS),
            cta_b=random.choice(cls.CTAS)
        )
