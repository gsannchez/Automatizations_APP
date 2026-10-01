class RetentionPredictor:
    """MVP simple version for retention prediction."""
    
    @staticmethod
    def predict_3s_retention(hook_text: str, hook_score: float) -> float:
        """Predicts the probability of retaining a user past the first 3 seconds."""
        base = 0.4
        length = len(hook_text.split())
        
        # Sweet spot is 5-12 words
        if 5 <= length <= 12:
            base += 0.2
            
        base += (hook_score / 100.0) * 0.3
        
        return min(base, 0.95)
