"""Pacing Controller service to adjust audio narrations and scene timings."""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PacingController:
    """Manages scene timings, speech velocity and inserts dramatic pauses for higher retention."""
    
    def optimize_timings(self, scenes: List[Dict[str, Any]], target_duration: float = 30.0) -> List[Dict[str, Any]]:
        """Distribute timings and insert [PAUSE] signals into scene texts to keep ideal pacing.
        
        Args:
            scenes: List of scene dictionaries (with "text" and "duration" fields).
            target_duration: Desired video duration in seconds.
            
        Returns:
            Optimized scenes list.
        """
        logger.info("Optimizing script pacing and audio-visual timings...")
        if not scenes:
            return []
            
        num_scenes = len(scenes)
        ideal_scene_duration = target_duration / num_scenes
        
        optimized_scenes = []
        for i, scene in enumerate(scenes):
            text = scene.get("text", "")
            words = text.split()
            word_count = len(words)
            
            # Target voice speed is 2.5 words per second
            estimated_voice_duration = word_count / 2.5
            
            # If scene text is long but duration is short, expand duration
            # If scene text is short but duration is long, inject a dramatic pause tag "[PAUSA]"
            final_duration = max(3.0, round(estimated_voice_duration))
            
            # Ensure pacing is exciting
            if final_duration > 8.0:
                # Truncate text or suggest split (handled by optimizer)
                pass
                
            # Inject dramatic pauses in hook scene or climax
            modified_text = text
            if i == 0 and not "[PAUSA]" in text and len(words) > 6:
                # Put a pause after the hook
                words.insert(5, "[PAUSA]")
                modified_text = " ".join(words)
                final_duration += 1.0 # Add 1s for the pause
                
            optimized_scenes.append({
                "text": modified_text,
                "duration": int(final_duration),
                "image_prompt": scene.get("image_prompt", "")
            })
            
        return optimized_scenes
