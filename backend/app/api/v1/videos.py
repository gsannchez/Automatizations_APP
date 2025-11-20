from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from ...core.database import engine
from ...models.generated_video import GeneratedVideo
from ...schemas.generated_video_schema import GeneratedVideoCreate, GeneratedVideoRead
from fastapi import BackgroundTasks

router = APIRouter()

@router.get("/", response_model=list[GeneratedVideoRead])
def list_videos():
    with Session(engine) as session:
        videos = session.exec(select(GeneratedVideo)).all()
        return videos

@router.post("/", response_model=GeneratedVideoRead)
def create_video(data: GeneratedVideoCreate):
    with Session(engine) as session:
        video = GeneratedVideo(**data.dict())
        session.add(video)
        session.commit()
        session.refresh(video)
        return video

@router.get("/{video_id}", response_model=GeneratedVideoRead)
def get_video(video_id: int):
    with Session(engine) as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            raise HTTPException(404, "Video not found")
        return video

@router.patch("/{video_id}", response_model=GeneratedVideoRead)
def update_video(video_id: int, status: str = None, file_path: str = None):
    with Session(engine) as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            raise HTTPException(404, "Video not found")

        if status is not None:
            video.status = status
        if file_path is not None:
            video.file_path = file_path

        session.add(video)
        session.commit()
        session.refresh(video)
        return video

@router.delete("/{video_id}")
def delete_video(video_id: int):
    with Session(engine) as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            raise HTTPException(404, "Video not found")
        session.delete(video)
        session.commit()
        return {"deleted": True}

from fastapi import BackgroundTasks, HTTPException
from ...services.video_generator import generate_and_store_video
from sqlmodel import Session
from ...core.database import engine
from ...models.generated_video import GeneratedVideo

@router.post("/{video_id}/generate")
def generate_video_endpoint(
    video_id: int,
    background_tasks: BackgroundTasks,
    music_file: str | None = None
):
    # verificar que existe el video
    with Session(engine) as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            raise HTTPException(404, "GeneratedVideo not found")

        # estado inicial
        video.status = "queued"
        session.add(video)
        session.commit()

    # lanzar generación en background
    background_tasks.add_task(generate_and_store_video, video_id, music_file)

    return {
        "message": "Video generation queued",
        "video_id": video_id,
        "music_file": music_file
    }

