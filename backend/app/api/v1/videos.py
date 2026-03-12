"""Video API endpoints — authenticated, owned, paginated.

All endpoints require a valid Bearer JWT.
Users can only read/modify their own videos (filtered by user_id).
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from uuid import UUID

from ...core.database import get_async_session
from ...models.generated_video import GeneratedVideo
from ...models.user import User
from ...schemas.generated_video_schema import (
    GeneratedVideoCreate,
    GeneratedVideoRead,
    GeneratedVideoStatus,
    GeneratedVideoPage,
)
from ...dependencies.auth import get_current_user
from ...tasks import process_video_workflow
from ...services.storage.key_builder import build_storage_key

router = APIRouter()


# ---------------------------------------------------------------------------
# List (paginated)
# ---------------------------------------------------------------------------

@router.get("/", response_model=GeneratedVideoPage)
async def list_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Return a paginated list of videos owned by the authenticated user."""
    base_filter = (
        GeneratedVideo.user_id == current_user.id,
        GeneratedVideo.is_deleted == False,
    )

    # Total count
    count_result = await session.execute(
        select(func.count(GeneratedVideo.id)).where(*base_filter)
    )
    total = count_result.scalar_one()

    # Page items
    offset = (page - 1) * limit
    result = await session.execute(
        select(GeneratedVideo)
        .where(*base_filter)
        .order_by(GeneratedVideo.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    items = result.scalars().all()

    return GeneratedVideoPage(items=list(items), total=total, page=page, limit=limit)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@router.post("/", response_model=GeneratedVideoRead)
async def create_video(
    data: GeneratedVideoCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new video record owned by the authenticated user."""
    video = GeneratedVideo(
        user_id=current_user.id,
        template_id=data.template_id,
        title=data.title,
        platform=data.platform,
        status="QUEUED",
        topic=data.topic,
        channel_id=data.channel_id,
    )
    session.add(video)
    await session.commit()
    await session.refresh(video)
    return video


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------

@router.get("/{video_id}", response_model=GeneratedVideoRead)
async def get_video(
    video_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Get a single video by ID. Returns 404 if not found or not owned."""
    video = await _get_owned_video(session, video_id, current_user.id)
    return video


# ---------------------------------------------------------------------------
# Status (lightweight — polling endpoint; contract must not change)
# ---------------------------------------------------------------------------

@router.get("/{video_id}/status", response_model=GeneratedVideoStatus)
async def get_video_status(
    video_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Lightweight status endpoint polled by the Angular frontend every 2 s."""
    video = await _get_owned_video(session, video_id, current_user.id)
    return video


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

@router.get("/{video_id}/download")
async def download_video(
    video_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Return a download URL for a completed video.

    The ``storage_key`` is never exposed directly; this endpoint is the single
    stable contract for file access. When cloud storage is introduced, only
    this endpoint changes — the frontend contract stays identical.

    Returns:
        HTTP 409 if video is not yet complete.
        HTTP 200 with ``{ download_url }`` when status is DONE.
    """
    video = await _get_owned_video(session, video_id, current_user.id)

    if video.status != "DONE":
        raise HTTPException(
            status_code=409,
            detail=f"Video is not ready for download (status: {video.status})",
        )

    # Build deterministic download URL from canonical storage key
    key = build_storage_key(video, "final.mp4")
    download_url = f"/media/{key}"
    return {"download_url": download_url}


# ---------------------------------------------------------------------------
# Update (partial)
# ---------------------------------------------------------------------------

@router.patch("/{video_id}", response_model=GeneratedVideoRead)
async def update_video(
    video_id: UUID,
    status: str = None,
    storage_key: str = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Update video fields. Only the owner may modify their video."""
    video = await _get_owned_video(session, video_id, current_user.id)

    if status is not None:
        video.status = status
    if storage_key is not None:
        video.storage_key = storage_key

    session.add(video)
    await session.commit()
    await session.refresh(video)
    return video


# ---------------------------------------------------------------------------
# Delete (soft)
# ---------------------------------------------------------------------------

@router.delete("/{video_id}")
async def delete_video(
    video_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Soft-delete a video. Only the owner may delete their video."""
    video = await _get_owned_video(session, video_id, current_user.id)

    video.is_deleted = True
    video.deleted_at = datetime.utcnow()
    session.add(video)
    await session.commit()

    return {"deleted": True}


# ---------------------------------------------------------------------------
# Generate (queue Celery task)
# ---------------------------------------------------------------------------

@router.post("/{video_id}/generate")
async def generate_video_endpoint(
    video_id: UUID,
    music_file: str | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Queue video generation via Celery orchestrator."""
    video = await _get_owned_video(session, video_id, current_user.id)

    # Reset to QUEUED so the orchestrator starts from scratch / resumes
    video.status = "QUEUED"
    session.add(video)
    await session.commit()

    process_video_workflow.delay(str(video_id))

    return {
        "message": "Video generation queued via Celery (Orchestrator)",
        "video_id": str(video_id),
        "music_file": music_file,
    }


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

async def _get_owned_video(
    session: AsyncSession,
    video_id: UUID,
    user_id: UUID,
) -> GeneratedVideo:
    """Fetch a non-deleted video that belongs to *user_id*.

    Returns HTTP 404 if not found OR not owned (security through obscurity).
    """
    result = await session.execute(
        select(GeneratedVideo).where(
            GeneratedVideo.id == video_id,
            GeneratedVideo.user_id == user_id,
            GeneratedVideo.is_deleted == False,
        )
    )
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video
