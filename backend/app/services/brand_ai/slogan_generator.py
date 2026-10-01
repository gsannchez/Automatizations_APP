"""
app/services/brand_ai/slogan_generator.py
"""
import logging
import random

logger = logging.getLogger(__name__)

class SloganGenerator:
    def generate(self, style: str) -> str:
        """Generates slogans heuristically."""
        slogans = {
            "cinematic": "Experience the Unseen.",
            "meme": "Laugh every day.",
            "horror": "Sleep with one eye open.",
            "emotional": "Feel every moment.",
            "documentary": "The truth unveiled."
        }
        return slogans.get(style.lower(), "Your daily content.")
