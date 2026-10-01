import copy
from typing import List, Dict
from .pacing_analyzer import PacingAnalyzer

class SceneRebalancer:
    """
    Rebalances scenes by splitting long scenes into smaller chunks.
    This forces the render engine to apply different camera motions or effects
    to each sub-scene, creating the illusion of a fast-paced cut.
    """
    
    @staticmethod
    def rebalance(scenes: List[Dict], style: str = "tiktok") -> List[Dict]:
        """
        Takes a list of scenes and splits them if they are too long.
        """
        max_dur = PacingAnalyzer.MAX_SCENE_DURATION_CINEMATIC if "cinematic" in style.lower() else PacingAnalyzer.MAX_SCENE_DURATION_TIKTOK
        
        rebalanced_scenes = []
        
        for scene in scenes:
            dur = scene.get("duration", 0)
            
            if dur <= max_dur:
                rebalanced_scenes.append(scene)
            else:
                # Need to split the scene
                # E.g., a 6s scene becomes two 3s sub-scenes
                # They will share the same image, but we can assign different 'motion_seed' or 'sub_index'
                # so the visual_fx engine knows to apply a whip pan or flash cut between them.
                
                num_splits = int((dur // max_dur) + 1)
                split_dur = dur / num_splits
                
                for i in range(num_splits):
                    new_scene = copy.deepcopy(scene)
                    new_scene["duration"] = split_dur
                    new_scene["is_sub_scene"] = True
                    new_scene["sub_index"] = i
                    rebalanced_scenes.append(new_scene)
                    
        return rebalanced_scenes
