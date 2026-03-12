"""Storage key builder for idempotent file handling."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.generated_video import GeneratedVideo

def build_storage_key(video: 'GeneratedVideo', filename: str) -> str:
    """Build a deterministic storage key prefix for video assets.
    
    Args:
        video: GeneratedVideo instance
        filename: Name of the file, e.g. 'final.mp4', 'images/0.png'
        
    Returns:
        str: Formatted storage key path `videos/{user_id}/{video_id}/{filename}`
    """
    user_id = video.user_id if video.user_id else "anonymous"
    return f"videos/{user_id}/{video.id}/{filename}"
