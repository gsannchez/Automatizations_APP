"""
app/services/ai_director/scene_supervisor.py

Phase 10: Wraps CinematicRulesEngine to validate complete scripts before generation.
"""
import logging
from typing import Dict, Any, List
from .cinematic_rules import CinematicRulesEngine

logger = logging.getLogger(__name__)

class SceneSupervisor:
    """
    Evaluates a script's scene flow against platform-specific cinematic rules.
    """
    def validate_script(self, script_data: Dict[str, Any], platform: str) -> List[str]:
        warnings = []
        scenes = script_data.get("scenes", [])
        
        if not scenes:
            return ["Script has no scenes."]
            
        # 1. Validate Durations
        duration_warnings = CinematicRulesEngine.validate_scene_durations(scenes, platform)
        warnings.extend(duration_warnings)
        
        # 2. Validate Transitions
        transition_warnings = CinematicRulesEngine.validate_transitions(scenes)
        warnings.extend(transition_warnings)
        
        # 3. Validate Prompt Complexity
        for i, scene in enumerate(scenes):
            prompt = scene.get("prompt", "")
            if not CinematicRulesEngine.validate_prompt_complexity(prompt):
                warnings.append(f"Scene {i} prompt is too complex. High risk of generation artifacts.")
                
        if warnings:
            logger.warning(f"[SceneSupervisor] Found {len(warnings)} cinematic rule violations.")
            
        return warnings
