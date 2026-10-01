from .video_generator_factory import VideoGeneratorFactory
from .motion_scheduler import MotionScheduler
from .video_cache import VideoCache

class HybridGenerator:
    """
    Decides when to use expensive AI video generation vs. cheap FFmpeg pseudo-motion.
    """
    
    def __init__(self):
        self.cache = VideoCache()
        
    def process_scene(self, scene_index: int, image_path: str, prompt: str, duration_sec: float, style: str, emotion: str) -> dict:
        """
        Returns a dict indicating how the scene should be rendered.
        """
        intensity = MotionScheduler.calculate_motion_intensity(scene_index, style, emotion)
        use_ai = MotionScheduler.requires_ai_video(intensity, style)
        
        result = {
            "image_path": image_path,
            "duration": duration_sec,
            "motion_intensity": intensity,
            "is_ai_video": use_ai,
            "video_path": None
        }
        
        if use_ai:
            seed = 42 # In reality, get from TemporalConsistencyEngine
            
            # Check cache
            cached = self.cache.get_cached_video(prompt, seed, style, duration_sec)
            if cached:
                print(f"🎬 [HybridGenerator] Cache HIT for scene {scene_index}")
                result["video_path"] = cached
            else:
                print(f"🎬 [HybridGenerator] Generating AI Video for scene {scene_index}...")
                generator = VideoGeneratorFactory.get_generator(style)
                generated_path = generator.generate(prompt, image_path, duration_sec, seed, style)
                
                # Save to cache
                self.cache.save_to_cache(generated_path, prompt, seed, style, duration_sec)
                result["video_path"] = generated_path
                
        return result
