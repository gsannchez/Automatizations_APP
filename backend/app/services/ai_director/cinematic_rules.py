"""
app/services/ai_director/cinematic_rules.py

Phase 10: Enforces foundational cinematic heuristics to prevent
poor aesthetic choices before rendering begins.
"""
from typing import Dict, List, Any

# Minimum scene lengths in seconds based on platform
MIN_SCENE_DURATION = {
    "tiktok": 1.5,
    "shorts": 1.5,
    "reels": 1.5,
    "youtube_long": 3.0,
}

# Maximum scene lengths before a cut is forced
MAX_SCENE_DURATION = {
    "tiktok": 4.0,
    "shorts": 4.5,
    "reels": 4.0,
    "youtube_long": 8.0,
}

# Transition limits
FORBIDDEN_TRANSITIONS = {
    "zoom_in": ["zoom_in", "pan_up"], # Don't zoom in twice in a row
    "pan_left": ["pan_right"],        # Avoid jarring back-and-forth
    "fade": ["fade", "dissolve"],     # Avoid double fades
}

# Prompt complexity limits (heuristic token count or comma count)
MAX_PROMPT_COMPLEXITY_SCORE = 15

class CinematicRulesEngine:
    @staticmethod
    def validate_scene_durations(scenes: List[Dict[str, Any]], platform: str) -> List[str]:
        """Returns a list of warnings for rule violations."""
        warnings = []
        min_len = MIN_SCENE_DURATION.get(platform, 2.0)
        max_len = MAX_SCENE_DURATION.get(platform, 5.0)
        
        for i, scene in enumerate(scenes):
            duration = scene.get("duration", 0)
            if duration < min_len:
                warnings.append(f"Scene {i} is too short ({duration}s < {min_len}s). Risk of flicker.")
            if duration > max_len:
                warnings.append(f"Scene {i} is too long ({duration}s > {max_len}s). Risk of viewer drop-off.")
                
        return warnings

    @staticmethod
    def validate_transitions(scenes: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        for i in range(1, len(scenes)):
            prev_trans = scenes[i-1].get("transition_out", "none")
            curr_trans = scenes[i].get("transition_in", "none")
            
            if curr_trans in FORBIDDEN_TRANSITIONS.get(prev_trans, []):
                warnings.append(
                    f"Forbidden transition combo: {prev_trans} -> {curr_trans} between scenes {i-1} and {i}."
                )
                
        return warnings

    @staticmethod
    def validate_prompt_complexity(prompt: str) -> bool:
        """Returns True if the prompt is safe, False if it's too complex and likely to artifact."""
        complexity = prompt.count(",") + (len(prompt.split()) / 10)
        return complexity <= MAX_PROMPT_COMPLEXITY_SCORE
