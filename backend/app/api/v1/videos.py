from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from ...core.database import engine
from ...models.generated_video import GeneratedVideo
from ...schemas.generated_video_schema import GeneratedVideoCreate, GeneratedVideoRead

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
