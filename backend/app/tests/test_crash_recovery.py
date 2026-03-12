import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
import sqlalchemy as sa
from sqlmodel import Session, select
from datetime import datetime

from app.core.database import get_sync_session, engine
from app.models.generated_video import GeneratedVideo
from app.models.template import Template
from app.models.video_job import VideoJob
from app.tasks import process_video_workflow, PIPELINE_STEPS

# We use sync session for the tests that set up the DB state quickly
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # Setup template
    with Session(engine) as session:
        # Check if template exists
        t = session.get(Template, "123e4567-e89b-12d3-a456-426614174000")
        if not t:
            try:
                # We simply bypass the setup if template FK can be anything
                pass
            except Exception:
                pass


@pytest.fixture
def db_session():
    with Session(engine) as session:
        yield session

class CrashException(Exception):
    pass

class MockTaskSelf:
    def retry(self, exc=None, countdown=None):
        raise CrashException("Worker crashed!")

def create_test_video(session: Session) -> str:
    # Use a dummy template_id, assuming foreign key constraints are handled or mocked
    # In SQLite during tests, FKs might be disabled, but let's be safe.
    from app.utils.uuid_utils import generate_uuid7
    vid = GeneratedVideo(
        id=generate_uuid7(),
        template_id=generate_uuid7(), # mock template ID
        title="Test crash",
        platform="TIKTOK",
        status="QUEUED"
    )
    session.add(vid)
    session.commit()
    session.refresh(vid)
    return str(vid.id)


@patch("app.tasks.generate_script")
@patch("app.tasks.VideoGenerator")
def test_normal_run(mock_vg, mock_script, db_session: Session):
    vid_id = create_test_video(db_session)
    mock_script.return_value = MagicMock(scenes=[MagicMock(dict=lambda: {"text": "hi"})])
    mock_vg.return_value.assemble_video.return_value = "videos/test/final.mp4"

    # Execute workflow
    process_video_workflow(MockTaskSelf(), vid_id)

    # Verify
    db_session.expire_all()
    video = db_session.get(GeneratedVideo, UUID(vid_id) if hasattr(vid_id, 'hex') else vid_id) # handle uuid casting if needed
    
    # We query as string implicitly handled by SQLModel/SQLAlchemy
    # But let's retrieve carefully
    video = db_session.execute(select(GeneratedVideo).where(GeneratedVideo.id == vid_id)).scalars().first()
    
    assert video.status == "DONE"
    from app.utils.progress_utils import get_progress_from_status
    assert get_progress_from_status(video.status) == 100
    assert video.storage_key == "videos/test/final.mp4"


@patch("app.tasks.generate_script")
@patch("app.tasks.VideoGenerator")
def test_crash_during_image_generation(mock_vg, mock_script, db_session: Session):
    """Crash at IMAGE_GENERATION and resume."""
    vid_id = create_test_video(db_session)
    
    # Mock script setup
    mock_script.return_value = MagicMock(scenes=[MagicMock(dict=lambda: {"text": "hi"})])
    
    # First run will crash at IMAGE_GENERATION
    original_has_completed = VideoJobService.has_completed_step if False else None # just reference tracker
    
    crash_state = {"crashed": False}
    
    def side_effect_step(*args, **kwargs):
        # We'll inject the failure inside the tasks loop by patching something inside it
        pass

    # We can patch job_service.mark_success to raise an error if step is IMAGE_GENERATION
    with patch("app.tasks.VideoJobService.mark_success") as mock_success:
        def crash_on_image(job_id):
            # We need to find the job step to know if it's IMAGE_GENERATION
            job = db_session.get(VideoJob, job_id)
            if job and job.step == "IMAGE_GENERATION" and not crash_state["crashed"]:
                crash_state["crashed"] = True
                raise Exception("Network Error in A1111")
            # manual success logic since we patched it
            if job:
                job.success = True
                db_session.add(job)
                db_session.commit()
                
        mock_success.side_effect = crash_on_image
        
        try:
            process_video_workflow(MockTaskSelf(), vid_id)
        except CrashException:
            pass # We crashed successfully
            
    assert crash_state["crashed"] == True
    
    # Now verify the state before resume
    db_session.expire_all()
    jobs = db_session.execute(select(VideoJob).where(VideoJob.video_id == vid_id)).scalars().all()
    assert any(j.step == "SCRIPTING" and j.success for j in jobs)
    
    # Run again without crash
    process_video_workflow(MockTaskSelf(), vid_id)
    db_session.expire_all()
    video = db_session.execute(select(GeneratedVideo).where(GeneratedVideo.id == vid_id)).scalars().first()
    assert video.status == "DONE"
    # Verify SCRIPTING was not repeated (only 1 success job)
    script_jobs = [j for j in db_session.execute(select(VideoJob).where(VideoJob.video_id == vid_id, VideoJob.step == "SCRIPTING")).scalars().all()]
    assert len(script_jobs) == 1


@patch("app.tasks.generate_script")
@patch("app.tasks.VideoGenerator")
def test_crash_during_encoding(mock_vg, mock_script, db_session: Session):
    vid_id = create_test_video(db_session)
    mock_script.return_value = MagicMock(scenes=[MagicMock(dict=lambda: {"text": "hi"})])
    
    crash_state = {"crashed": False}
    with patch("app.tasks.VideoJobService.mark_success") as mock_success:
        def crash_on_enc(job_id):
            job = db_session.get(VideoJob, job_id)
            if job and job.step == "ENCODING" and not crash_state["crashed"]:
                crash_state["crashed"] = True
                raise Exception("FFmpeg crash")
            if job:
                job.success = True
                db_session.add(job)
                db_session.commit()
                
        mock_success.side_effect = crash_on_enc
        
        try:
            process_video_workflow(MockTaskSelf(), vid_id)
        except CrashException:
            pass 
            
    # Resume
    process_video_workflow(MockTaskSelf(), vid_id)
    db_session.expire_all()
    video = db_session.execute(select(GeneratedVideo).where(GeneratedVideo.id == vid_id)).scalars().first()
    assert video.status == "DONE"

def test_video_job_integrity(db_session: Session):
    # Test 4: Verify SQL directly
    # Using the last video created in the db
    video = db_session.execute(select(GeneratedVideo).order_by(GeneratedVideo.created_at.desc())).scalars().first()
    vid_id = video.id
    
    jobs = db_session.execute(
        sa.text("SELECT step, success FROM videojob WHERE video_id = :v ORDER BY started_at"),
        {"v": str(vid_id)}
    ).fetchall()
    
    # We should have all steps in the frozen pipeline successful at least once
    steps_found = set([j.step for j in jobs if j.success])
    assert "IMAGE_GENERATION" in steps_found
    assert "SCRIPTING" in steps_found
    assert "DONE" in steps_found
