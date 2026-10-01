class TemporalConsistencyEngine:
    """
    Strategies to maintain temporal consistency across AI generated video frames.
    """
    
    @staticmethod
    def get_seed_for_scene(base_seed: int, scene_index: int, lock_seed: bool = True) -> int:
        """
        If lock_seed is True, reuses the same seed to maintain character/background consistency
        across different shots of the same video.
        """
        if lock_seed:
            return base_seed
        return base_seed + scene_index

    @staticmethod
    def get_latent_reuse_params() -> dict:
        """
        Returns parameters for FreeU or similar latent blending techniques 
        to reduce flickering.
        """
        return {
            "use_freeu": True,
            "b1": 1.2,
            "b2": 1.4,
            "s1": 0.9,
            "s2": 0.2
        }
