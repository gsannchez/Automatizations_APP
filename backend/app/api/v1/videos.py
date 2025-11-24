from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_session
from ...models.generated_video import GeneratedVideo
from ...schemas.generated_video_schema import GeneratedVideoCreate, GeneratedVideoRead
from ...tasks import generate_video_task

router = APIRouter()

@router.get("/", response_model=list[GeneratedVideoRead])
async def list_videos(session: AsyncSession = Depends(get_session)):
    result = await session.exec(select(GeneratedVideo))
    videos = result.all()
    return videos

@router.post("/", response_model=GeneratedVideoRead)
async def create_video(data: GeneratedVideoCreate, session: AsyncSession = Depends(get_session)):
    video = GeneratedVideo(**data.dict())
    session.add(video)
    await session.commit()
    await session.refresh(video)
    return video

@router.get("/{video_id}", response_model=GeneratedVideoRead)
async def get_video(video_id: int, session: AsyncSession = Depends(get_session)):
    video = await session.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(404, "Video not found")
    return video

@router.patch("/{video_id}", response_model=GeneratedVideoRead)
async def update_video(video_id: int, status: str = None, file_path: str = None, session: AsyncSession = Depends(get_session)):
    video = await session.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    if status is not None:
        video.status = status
    if file_path is not None:
        video.file_path = file_path

    session.add(video)
    await session.commit()
    await session.refresh(video)
    return video

@router.delete("/{video_id}")
async def delete_video(video_id: int, session: AsyncSession = Depends(get_session)):
    video = await session.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(404, "Video not found")
    await session.delete(video)
    await session.commit()
    return {"deleted": True}

@router.post("/{video_id}/generate")
async def generate_video_endpoint(
    video_id: int,
    music_file: str | None = None,
    session: AsyncSession = Depends(get_session)
):
    # verificar que existe el video
    video = await session.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(404, "GeneratedVideo not found")

    # estado inicial
    video.status = "queued"
    session.add(video)
    await session.commit()

    # lanzar generación en background con Celery
    generate_video_task.delay(video_id)

    return {
        "message": "Video generation queued via Celery",
        "video_id": video_id,
        "music_file": music_file
    }
