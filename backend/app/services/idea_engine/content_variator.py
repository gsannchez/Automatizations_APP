class ContentVariator:
    """Generates variants of a core idea."""
    
    @staticmethod
    def generate_variants(base_idea: dict) -> list:
        """Returns 3-5 variants (short, emotional, shock, cinematic)."""
        core = base_idea["core_idea"]
        return [
            {
                "variant": "short",
                "idea": f"{core}, but optimized for a 15s short attention span.",
                "duration": 15
            },
            {
                "variant": "emotional",
                "idea": f"{core}, focusing heavily on the human element and empathy.",
                "duration": 45
            },
            {
                "variant": "shock",
                "idea": f"{core}, starting with a jarring, unexpected revelation.",
                "duration": 30
            },
            {
                "variant": "cinematic",
                "idea": f"{core}, told like a movie trailer with dramatic pacing.",
                "duration": 60
            }
        ]
