"""Phase 8: Campaign Manager — episodic content series with narrative continuity."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ...models.orchestration import Campaign
from ...utils.uuid_utils import generate_uuid7

logger = logging.getLogger(__name__)


class CampaignManager:
    """
    Manages episodic video series with persistent storyline memory.
    Supports recurring characters, sequel generation, and episode tracking.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_campaign(
        self,
        name: str,
        total_episodes: int = 20,
        recurring_characters: Optional[List[str]] = None,
        initial_storyline: Optional[Dict[str, Any]] = None,
    ) -> Campaign:
        campaign = Campaign(
            name=name,
            total_episodes=total_episodes,
            current_episode=0,
            recurring_characters=recurring_characters or [],
            storyline_persistence=initial_storyline or {"arc": "introduction", "events": []},
        )
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        logger.info(f"[CampaignManager] Created campaign '{name}' with {total_episodes} episodes.")
        return campaign

    def get_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        return self.session.get(Campaign, campaign_id)

    def get_by_name(self, name: str) -> Optional[Campaign]:
        return self.session.exec(
            select(Campaign).where(Campaign.name == name)
        ).first()

    def advance_episode(self, campaign_id: UUID, episode_summary: Dict[str, Any]) -> Campaign:
        campaign = self.session.get(Campaign, campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found.")
        if campaign.current_episode >= campaign.total_episodes:
            logger.warning(f"[CampaignManager] Campaign '{campaign.name}' already completed.")
            return campaign

        # Update storyline persistence
        storyline = campaign.storyline_persistence or {"arc": "introduction", "events": []}
        events: List[Dict] = storyline.get("events", [])
        events.append({
            "episode": campaign.current_episode + 1,
            "ts": datetime.utcnow().isoformat(),
            **episode_summary,
        })
        storyline["events"] = events[-30:]  # retain last 30 episode summaries

        # Arc progression
        progress = (campaign.current_episode + 1) / campaign.total_episodes
        if progress < 0.3:
            storyline["arc"] = "introduction"
        elif progress < 0.7:
            storyline["arc"] = "development"
        elif progress < 0.9:
            storyline["arc"] = "climax"
        else:
            storyline["arc"] = "resolution"

        campaign.current_episode += 1
        campaign.storyline_persistence = storyline
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        logger.info(f"[CampaignManager] Campaign '{campaign.name}' advanced to episode {campaign.current_episode}/{campaign.total_episodes} | arc={storyline['arc']}")
        
        # Phase 11.1 Event integration
        from .event_bus import get_event_bus, EventType
        import asyncio
        bus = get_event_bus()
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(bus.publish(EventType.UNIVERSE_UPDATED, {"campaign_id": str(campaign.id), "episode": campaign.current_episode}))
        except RuntimeError:
            pass # Not in an event loop

        return campaign

    def build_episode_prompt(self, campaign: Campaign) -> str:
        """Generate a context-aware prompt fragment for the next episode."""
        storyline = campaign.storyline_persistence or {}
        arc = storyline.get("arc", "introduction")
        events = storyline.get("events", [])
        characters = ", ".join(campaign.recurring_characters or ["the protagonist"])
        last_event = events[-1].get("summary", "an unexpected turn") if events else "the beginning"
        ep_num = campaign.current_episode + 1

        return (
            f"[Campaign: {campaign.name} | Episode {ep_num}/{campaign.total_episodes}]\n"
            f"Story Arc: {arc.upper()}\n"
            f"Recurring characters: {characters}\n"
            f"Last episode summary: {last_event}\n"
            f"Continue the story logically from the previous episode. Maintain character consistency."
        )

    def list_campaigns(self) -> List[Dict[str, Any]]:
        campaigns = self.session.exec(select(Campaign)).all()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "total_episodes": c.total_episodes,
                "current_episode": c.current_episode,
                "arc": (c.storyline_persistence or {}).get("arc", "unknown"),
                "progress_pct": round((c.current_episode / c.total_episodes) * 100, 1),
            }
            for c in campaigns
        ]
