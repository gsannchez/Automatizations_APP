from .retention_predictor import RetentionPredictor

class HookOptimizer:
    """Pre-script optimization of the hook."""

    URGENCY_WORDS = ["now", "stop", "wait", "watch", "listen", "look", "attention"]
    CURIOSITY_TRIGGERS = ["secret", "truth", "why", "how", "reason", "never", "always"]
    CONTRADICTIONS = ["but", "actually", "instead", "wrong", "lie"]

    @classmethod
    def optimize(cls, idea_dict: dict) -> dict:
        """
        Analyzes the generated hook and outputs optimization details.
        """
        hook = idea_dict.get("hook", "").lower()
        words = hook.split()
        
        score = 50.0
        fixes = []
        
        # Length check
        if len(words) < 3:
            fixes.append("Hook is too short, add curiosity triggers.")
            score -= 10
        elif len(words) > 15:
            fixes.append("Hook is too long, make it punchier (under 15 words).")
            score -= 10
        else:
            score += 10
            
        # Urgency
        if any(w in hook for w in cls.URGENCY_WORDS):
            score += 15
        else:
            fixes.append("Add urgency words like 'wait' or 'watch'.")
            
        # Curiosity
        if any(w in hook for w in cls.CURIOSITY_TRIGGERS):
            score += 15
        else:
            fixes.append("Add curiosity triggers like 'secret' or 'truth'.")
            
        # Contradiction
        if any(w in hook for w in cls.CONTRADICTIONS):
            score += 10
            
        score = min(max(score, 0.0), 100.0)
        
        predicted_retention = RetentionPredictor.predict_3s_retention(hook, score)
        drop_risk = max(0.0, 1.0 - predicted_retention)
        
        return {
            "hook_score": score,
            "drop_risk_3s": drop_risk,
            "fixes": fixes,
            "predicted_retention_3s": predicted_retention
        }
