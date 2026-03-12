from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from ...core.database import sync_engine
from ...models.channel import Channel
from ...schemas.channel_schema import ChannelCreate, ChannelRead

router = APIRouter(tags=["Channels"])

@router.get("/", response_model=list[ChannelRead])
def list_channels():
    with Session(sync_engine) as session:
        channels = session.exec(select(Channel)).all()
        return channels

@router.post("/", response_model=ChannelRead)
def create_channel(data: ChannelCreate):
    with Session(sync_engine) as session:
        channel = Channel(**data.dict())
        session.add(channel)
        session.commit()
        session.refresh(channel)
        return channel

@router.get("/{channel_id}", response_model=ChannelRead)
def get_channel(channel_id: int):
    with Session(sync_engine) as session:
        channel = session.get(Channel, channel_id)
        if not channel:
            raise HTTPException(404, "Channel not found")
        return channel

@router.delete("/{channel_id}")
def delete_channel(channel_id: int):
    with Session(sync_engine) as session:
        channel = session.get(Channel, channel_id)
        if not channel:
            raise HTTPException(404, "Channel not found")
        session.delete(channel)
        session.commit()
        return {"deleted": True}
