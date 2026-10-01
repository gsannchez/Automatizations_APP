import random

class StyleRecommender:
    """Recommends visual styles based on topic and emotion."""
    
    @staticmethod
    def recommend(topic: str, emotion: str, platform: str) -> str:
        topic_lower = topic.lower()
        if any(w in topic_lower for w in ["dog", "rescue", "police", "arrest"]):
            return "BODYCAM"
        if any(w in topic_lower for w in ["conspiracy", "ghost", "caught", "camera"]):
            return "CCTV"
        if any(w in topic_lower for w in ["anime", "motivation", "naruto"]):
            return "ANIME_EDIT"
        if emotion == "sad" or "heartbreak" in topic_lower:
            return "CINEMATIC_AI"
            
        return "TIKTOK_NATIVE"
