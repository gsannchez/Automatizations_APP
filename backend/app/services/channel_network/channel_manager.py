"""
app/services/channel_network/channel_manager.py
"""
import logging
from uuid import UUID
from sqlmodel import Session, select
from app.models.media_network import ChannelProfile

logger = logging.getLogger(__name__)

class ChannelManager:
    def __init__(self, session: Session):
        self.session = session

    def create_channel(self, name: str, niche: str, tone: str, platform: str, upload_frequency: str) -> ChannelProfile:
        logger.info(f"Creating channel: {name}")
        channel = ChannelProfile(
            name=name,
            niche=niche,
            tone=tone,
            platform=platform,
            upload_frequency=upload_frequency,
            active=True
        )
        self.session.add(channel)
        self.session.commit()
        return channel

    def set_channel_status(self, channel_id: UUID, active: bool):
        channel = self.session.get(ChannelProfile, channel_id)
        if channel:
            channel.active = active
            self.session.commit()

    def track_growth_score(self, channel_id: UUID, new_score: float):
        channel = self.session.get(ChannelProfile, channel_id)
        if channel:
            channel.growth_score = new_score
            self.session.commit()
