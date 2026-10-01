class EmotionAnalyzer:
    """MVP emotion tagging helper."""
    
    @staticmethod
    def analyze(text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["sad", "cry", "tragic", "heartbreak"]):
            return "sad"
        elif any(w in text_lower for w in ["angry", "rage", "mad", "furious"]):
            return "angry"
        elif any(w in text_lower for w in ["shock", "wow", "crazy", "unbelieve", "insane"]):
            return "shocked"
        return "neutral"
