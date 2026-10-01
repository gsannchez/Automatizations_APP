class FormatMapper:
    """Maps trend topics to internal visual formats."""

    _MAPPINGS = {
        "dog rescue": "BODYCAM",
        "crime footage": "CCTV",
        "movie recap": "CINEMATIC",
        "reddit story": "STORYTIME",
        "creepy pasta": "HORROR",
        "news flash": "NEWS",
    }

    @classmethod
    def map_format(cls, topic: str, default: str = "TIKTOK_NATIVE") -> str:
        """
        Returns the mapped format for a given topic, 
        or the default if no mapping is found.
        """
        topic_lower = topic.lower()
        for key, fmt in cls._MAPPINGS.items():
            if key in topic_lower:
                return fmt
        return default
