import random

class CameraMotionEngine:
    """
    Generates dynamic camera motion filters (zoompan, shake)
    for still images to make them feel alive.
    """
    
    @staticmethod
    def get_motion_filter(duration: float, width: int = 1080, height: int = 1920, style: str = "tiktok", sub_index: int = 0) -> str:
        """
        Returns a zoompan filter string. 
        `sub_index` is used if a scene was split; subsequent splits should have different motions.
        """
        fps = 30
        frames = int(duration * fps)
        
        # Base motions
        motions = [
            # Slow zoom in center
            f"zoompan=z='min(zoom+0.0015,1.5)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}",
            # Slow zoom out center
            f"zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}",
            # Pan left to right
            f"zoompan=z='1.2':d={frames}:x='if(lte(on,1),(iw/zoom/2),x+1)':y='ih/2-(ih/zoom/2)':s={width}x{height}",
            # Pan right to left
            f"zoompan=z='1.2':d={frames}:x='if(lte(on,1),(iw-(iw/zoom/2)),x-1)':y='ih/2-(ih/zoom/2)':s={width}x{height}"
        ]
        
        # If it's a cinematic style, bias towards slow center zooms
        if "cinematic" in style.lower():
            motion = random.choice(motions[:2])
        else:
            # For TikTok, mix it up. Use sub_index to seed the choice so rebalanced scenes look different
            random.seed(hash(f"{duration}_{sub_index}"))
            motion = random.choice(motions)
            
        return motion
