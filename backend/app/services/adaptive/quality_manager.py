from enum import Enum

class QualityTier(Enum):
    ULTRA = "ultra"
    HIGH = "high"
    BALANCED = "balanced"
    PERFORMANCE = "performance"
    SAFE_MODE = "safe_mode"

class QualityManager:
    """
    Manages the current rendering quality tier based on system resources.
    """
    _current_tier = QualityTier.HIGH
    
    @classmethod
    def get_tier(cls) -> QualityTier:
        return cls._current_tier
        
    @classmethod
    def downgrade(cls):
        """Downgrades quality if system is struggling."""
        tiers = list(QualityTier)
        idx = tiers.index(cls._current_tier)
        if idx < len(tiers) - 1:
            cls._current_tier = tiers[idx + 1]
            
    @classmethod
    def reset(cls):
        cls._current_tier = QualityTier.HIGH
