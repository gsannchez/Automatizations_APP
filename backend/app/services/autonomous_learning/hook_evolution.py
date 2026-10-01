import random

class HookEvolution:
    """Modifies hooks automatically based on previous results."""
    
    TEMPLATES = [
        "Nobody understood why {subject} {action} until...",
        "The secret behind {subject} finally revealed.",
        "Why {subject} is actually {unexpected_trait}.",
        "I found out the truth about {subject} and it's terrifying."
    ]
    
    @classmethod
    def evolve(cls, base_hook: str, idea_dict: dict) -> str:
        """Evolves the hook using templates, mutations, and weighted randomness."""
        subject = idea_dict.get("topic", "this")
        
        # 30% chance to mutate completely to a proven template
        if random.random() < 0.3:
            template = random.choice(cls.TEMPLATES)
            action = "did this"
            trait = "insane"
            return template.format(subject=subject, action=action, unexpected_trait=trait)
            
        # Otherwise, tweak intensity
        mutated_hook = base_hook
        if "!" not in mutated_hook:
            mutated_hook += "!"
            
        return mutated_hook
