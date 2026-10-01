"""
app/services/ai_director/creative_decision_engine.py

Phase 10: Makes creative mutations to scripts and prompts based on 
cinematic rules or failure analysis.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class CreativeDecisionEngine:
    def optimize_script(self, script_data: Dict[str, Any], warnings: List[str]) -> Dict[str, Any]:
        """Applies heuristic fixes to the script based on validation warnings."""
        if not warnings:
            return script_data
            
        logger.info("[CreativeDecisionEngine] Optimizing script to resolve warnings.")
        
        scenes = script_data.get("scenes", [])
        for i, scene in enumerate(scenes):
            # Example fix: shorten scenes that are too long
            duration = scene.get("duration", 0)
            if duration > 5.0:
                scene["duration"] = 4.5
                logger.debug(f"Trimmed scene {i} duration to 4.5s")
                
            # Example fix: replace complex transitions with simple cuts
            if scene.get("transition_in") in ["zoom_in", "pan_left"]:
                scene["transition_in"] = "cut"
                logger.debug(f"Simplified transition for scene {i}")
                
        script_data["scenes"] = scenes
        return script_data

    def mutate_for_regeneration(self, original_prompt: str, failure_reasons: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determines how to change the prompt or settings based on why the render failed.
        """
        mutation = {
            "original": original_prompt,
            "new_prompt": original_prompt,
            "strategy": "simplify",
            "camera_motion": "static"
        }
        
        if not failure_reasons:
            return mutation
            
        if "motion_blur" in failure_reasons or "flicker" in failure_reasons:
            mutation["strategy"] = "reduce_motion"
            mutation["camera_motion"] = "static"
            # Attempt to append stabilization keywords
            mutation["new_prompt"] += ", high quality, sharp focus, slow motion"
            
        elif "artifacting" in failure_reasons:
            mutation["strategy"] = "simplify_prompt"
            # Strip out complex details (naive heuristic for now)
            words = original_prompt.split()
            if len(words) > 15:
                mutation["new_prompt"] = " ".join(words[:15]) + ", cinematic lighting"
                
        elif "warped_face" in failure_reasons:
            mutation["strategy"] = "face_fix"
            mutation["new_prompt"] += ", perfect anatomy, detailed face, symmetrical"
            
        return mutation
