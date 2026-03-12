"""VideoJob service for workflow step tracking.

Uses sync database session for Celery compatibility.
"""
from sqlalchemy.orm import Session
from app.models.video_job import VideoJob
from app.models.generated_video import GeneratedVideo
from datetime import datetime
from typing import Optional
from uuid import UUID


class VideoJobService:
    """Service for managing VideoJob records in Celery tasks."""
    
    def __init__(self, session: Session):
        """Initialize with sync database session.
        
        Args:
            session: Sync SQLAlchemy session from get_sync_session()
        """
        self.session = session
    
    def create_job(self, video_id: UUID, step: str) -> VideoJob:
        """Create a new VideoJob record for a workflow step.
        
        Args:
            video_id: UUID of the video
            step: Workflow step (e.g., "SCRIPTING", "IMAGE_GENERATION")
            
        Returns:
            VideoJob: Created job record
        """
        job = VideoJob(
            video_id=video_id,
            step=step,
            started_at=datetime.utcnow(),
            success=False
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job
    
    def mark_success(self, job_id: UUID) -> None:
        """Mark a job as successfully completed.
        
        Args:
            job_id: UUID of the job
        """
        job = self.session.get(VideoJob, job_id)
        if job:
            job.ended_at = datetime.utcnow()
            job.success = True
            self.session.commit()
    
    def mark_failure(self, job_id: UUID, error: str) -> None:
        """Mark a job as failed with error message.
        
        Args:
            job_id: UUID of the job
            error: Error message
        """
        job = self.session.get(VideoJob, job_id)
        if job:
            job.ended_at = datetime.utcnow()
            job.success = False
            job.error_message = error
            self.session.commit()
    
    def get_last_successful_step(self, video_id: UUID) -> Optional[str]:
        """Get the last successfully completed step for a video.
        
        Args:
            video_id: UUID of the video
            
        Returns:
            Optional[str]: Last successful step name, or None if no steps completed
        """
        jobs = self.session.query(VideoJob).filter(
            VideoJob.video_id == video_id,
            VideoJob.success == True
        ).order_by(VideoJob.ended_at.desc()).all()
        
        if jobs:
            return jobs[0].step
        return None
    
    def get_failed_step(self, video_id: UUID) -> Optional[str]:
        """Get the step where failure occurred.
        
        Args:
            video_id: UUID of the video
            
        Returns:
            Optional[str]: Failed step name, or None if no failures
        """
        jobs = self.session.query(VideoJob).filter(
            VideoJob.video_id == video_id,
            VideoJob.success == False,
            VideoJob.ended_at.isnot(None)
        ).order_by(VideoJob.ended_at.desc()).all()
        
        if jobs:
            return jobs[0].step
        return None
    
    def has_completed_step(self, video_id: UUID, step: str) -> bool:
        """Check if a specific step has been completed successfully.
        
        Args:
            video_id: UUID of the video
            step: Step name to check
            
        Returns:
            bool: True if step completed successfully
        """
        job = self.session.query(VideoJob).filter(
            VideoJob.video_id == video_id,
            VideoJob.step == step,
            VideoJob.success == True
        ).first()
        
        return job is not None
