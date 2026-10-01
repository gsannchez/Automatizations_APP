"""Clips API — /api/v1/clips/

Endpoints for intelligent clip extraction from long-form video files.
Handles scene detection, transcription, highlight scoring and vertical reformatting.
"""
import logging
import os
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from app.core.database import get_sync_session
from app.models.viral_intelligence import ClipAnalysis
from app.services.clips.clip_extractor import ClipExtractor
from app.services.clips.scene_detector import SceneDetector
from app.services.clips.whisper_service import WhisperService
from app.services.clips.highlight_detector import HighlightDetector
from app.services.clips.commentary_generator import CommentaryGenerator

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Clips"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ClipAnalyzeRequest(BaseModel):
    source_video_path: str = Field(
        ...,
        description="Absolute or relative path to the source video file on the server.",
        example="media/sources/movie.mp4",
    )
    output_dir: str = Field(
        default="media/clips",
        description="Directory where extracted vertical clips will be saved.",
    )
    max_clips: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of highlight clips to extract.",
    )
    min_clip_duration: float = Field(
        default=8.0,
        description="Minimum clip duration in seconds.",
    )
    max_clip_duration: float = Field(
        default=60.0,
        description="Maximum clip duration in seconds.",
    )
    generate_commentary: bool = Field(
        default=True,
        description="Generate automatic TikTok-style commentary for each clip.",
    )


class ClipAnalysisResponse(BaseModel):
    id: UUID
    source_video_path: str
    clip_path: str
    start_time: float
    end_time: float
    highlight_score: float
    transcript: str
    emotional_tone: str
    commentary: Optional[str] = None

    class Config:
        from_attributes = True


class AnalyzeJobResponse(BaseModel):
    status: str
    message: str
    source_video: str
    clips_requested: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/analyze",
    response_model=AnalyzeJobResponse,
    summary="Analyze a video and extract viral highlight clips",
    description=(
        "Uploads a video path for processing. The system will: "
        "1) detect scene cuts, 2) transcribe with Whisper, "
        "3) score highlights by emotional impact, 4) extract top clips in 9:16 vertical format, "
        "5) optionally generate commentary. Runs as a background task."
    ),
)
async def analyze_video(
    body: ClipAnalyzeRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_sync_session),
):
    """Trigger full clip analysis pipeline in the background."""
    # Validate source file exists
    if not os.path.exists(body.source_video_path):
        raise HTTPException(
            status_code=404,
            detail=f"Source video not found at path: {body.source_video_path}",
        )

    os.makedirs(body.output_dir, exist_ok=True)

    def _run_pipeline():
        try:
            logger.info(f"Starting clip extraction pipeline for: {body.source_video_path}")

            # 1. Scene detection
            detector = SceneDetector()
            scenes = detector.detect_scenes(body.source_video_path)
            logger.info(f"Detected {len(scenes)} scenes.")

            # 2. Transcription
            whisper = WhisperService()
            transcript_data = whisper.transcribe(body.source_video_path)

            # 3. Highlight scoring
            highlight_detector = HighlightDetector()
            highlights = highlight_detector.detect_highlights(
                scenes=scenes,
                transcript_data=transcript_data,
                max_clips=body.max_clips,
                min_duration=body.min_clip_duration,
                max_duration=body.max_clip_duration,
            )

            # 4. Extract and convert clips to vertical
            extractor = ClipExtractor()
            commentary_gen = CommentaryGenerator() if body.generate_commentary else None

            for highlight in highlights:
                clip_filename = f"clip_{highlight['scene_index']:03d}_{int(highlight['start_time'])}s.mp4"
                clip_path = os.path.join(body.output_dir, clip_filename)

                extracted_path = extractor.extract_clip(
                    source_path=body.source_video_path,
                    output_path=clip_path,
                    start_time=highlight["start_time"],
                    end_time=highlight["end_time"],
                    vertical=True,
                )

                commentary = None
                if commentary_gen and extracted_path:
                    commentary = commentary_gen.generate(
                        transcript=highlight.get("transcript", ""),
                        emotional_tone=highlight.get("emotional_tone", "neutral"),
                    )

                # Persist to DB
                clip_record = ClipAnalysis(
                    source_video_path=body.source_video_path,
                    clip_path=extracted_path or clip_path,
                    start_time=highlight["start_time"],
                    end_time=highlight["end_time"],
                    highlight_score=highlight.get("highlight_score", 0.0),
                    transcript=highlight.get("transcript", ""),
                    emotional_tone=highlight.get("emotional_tone", "neutral"),
                )
                session.add(clip_record)

            session.commit()
            logger.info(f"Clip extraction complete: {len(highlights)} clips saved.")

        except Exception as e:
            logger.error(f"Clip pipeline failed: {e}", exc_info=True)

    background_tasks.add_task(_run_pipeline)

    return AnalyzeJobResponse(
        status="processing",
        message=(
            f"Clip analysis started for '{body.source_video_path}'. "
            f"Check /api/v1/clips/ to retrieve results once processing completes."
        ),
        source_video=body.source_video_path,
        clips_requested=body.max_clips,
    )


@router.get(
    "/",
    response_model=List[ClipAnalysisResponse],
    summary="List all extracted clip analyses",
)
async def list_clips(
    limit: int = Query(20, ge=1, le=100),
    source_video: Optional[str] = Query(None, description="Filter by source video path"),
    session: Session = Depends(get_sync_session),
):
    """Return all ClipAnalysis records, ordered by highlight score descending."""
    query = (
        select(ClipAnalysis)
        .order_by(ClipAnalysis.highlight_score.desc())  # type: ignore
        .limit(limit)
    )
    clips = session.exec(query).all()

    if source_video:
        clips = [c for c in clips if source_video in c.source_video_path]

    return clips


@router.get(
    "/{clip_id}",
    response_model=ClipAnalysisResponse,
    summary="Get a specific clip analysis by ID",
)
async def get_clip(
    clip_id: UUID,
    session: Session = Depends(get_sync_session),
):
    """Retrieve a single ClipAnalysis by its UUID."""
    clip = session.get(ClipAnalysis, clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip analysis not found.")
    return clip


@router.delete(
    "/{clip_id}",
    summary="Delete a clip analysis record",
    status_code=204,
)
async def delete_clip(
    clip_id: UUID,
    delete_file: bool = Query(False, description="Also delete the clip file from disk."),
    session: Session = Depends(get_sync_session),
):
    """Remove a ClipAnalysis record, optionally deleting the file on disk."""
    clip = session.get(ClipAnalysis, clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip analysis not found.")

    if delete_file and os.path.exists(clip.clip_path):
        try:
            os.remove(clip.clip_path)
            logger.info(f"Deleted clip file: {clip.clip_path}")
        except Exception as e:
            logger.warning(f"Could not delete file {clip.clip_path}: {e}")

    session.delete(clip)
    session.commit()
