"""Video repository service."""
from sqlalchemy.orm import Session
from app.models.generated_video import GeneratedVideo
from datetime import datetime

def soft_delete_video(session: Session, video: GeneratedVideo) -> None:
    """Soft delete a video record.
    
    Args:
        session: Database session
        video: Video instance to delete
    """
    video.is_deleted = True
    video.deleted_at = datetime.utcnow()
    session.add(video)
    session.commit()
