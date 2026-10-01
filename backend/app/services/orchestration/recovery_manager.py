"""Phase 8: Auto Recovery Manager — detects dead workers and re-hydrates pipelines."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlmodel import Session, select

from ...models.generated_video import GeneratedVideo, PipelineState
from ...models.orchestration import AgentMemoryRecord, AgentState
from ...utils.uuid_utils import generate_uuid7

logger = logging.getLogger(__name__)

STUCK_THRESHOLD_MINUTES = 30


class RecoveryManager:
    """
    Scans for stuck pipelines and dead agents, then re-queues or resets them.
    Should be called periodically by the scheduler or generation loop.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_stuck_videos(self) -> List[GeneratedVideo]:
        """Find videos stuck in a non-terminal state for over the threshold."""
        cutoff = datetime.utcnow() - timedelta(minutes=STUCK_THRESHOLD_MINUTES)
        stuck = self.session.exec(
            select(GeneratedVideo).where(
                GeneratedVideo.status.notin_(["DONE", "FAILED"]),
                GeneratedVideo.updated_at < cutoff,
            )
        ).all()
        return stuck

    def recover_stuck_videos(self) -> Dict[str, Any]:
        """Mark stuck videos as FAILED so the user can retry or the loop can re-queue."""
        stuck = self.find_stuck_videos()
        if not stuck:
            logger.info("[RecoveryManager] No stuck videos found.")
            return {"recovered": 0, "ids": []}

        recovered_ids = []
        for video in stuck:
            logger.warning(
                f"[RecoveryManager] Recovering stuck video {video.id} "
                f"(state={video.status}, last_update={video.updated_at})"
            )
            video.status = PipelineState.FAILED.value
            video.error_step = "RECOVERY"
            video.error_message = f"Auto-recovered by RecoveryManager after {STUCK_THRESHOLD_MINUTES}min timeout."
            self.session.add(video)
            recovered_ids.append(str(video.id))

        self.session.commit()
        logger.info(f"[RecoveryManager] Recovered {len(recovered_ids)} stuck videos.")
        return {"recovered": len(recovered_ids), "ids": recovered_ids}

    def find_failed_agents(self) -> List[AgentMemoryRecord]:
        """Return agents currently in FAILED state."""
        return self.session.exec(
            select(AgentMemoryRecord).where(AgentMemoryRecord.state == AgentState.FAILED.value)
        ).all()

    def reset_failed_agents(self) -> Dict[str, Any]:
        """Reset FAILED agents back to IDLE so they can recover."""
        failed = self.find_failed_agents()
        if not failed:
            return {"reset": 0, "agents": []}

        agent_names = []
        for agent in failed:
            logger.info(f"[RecoveryManager] Resetting agent '{agent.agent_name}' from FAILED -> IDLE")
            agent.state = AgentState.IDLE.value
            agent.updated_at = datetime.utcnow()
            errors: List[str] = agent.recent_errors or []
            errors.append(f"{datetime.utcnow().isoformat()}: AUTO_RESET by RecoveryManager")
            agent.recent_errors = errors[-20:]
            self.session.add(agent)
            agent_names.append(agent.agent_name)

        self.session.commit()
        return {"reset": len(agent_names), "agents": agent_names}

    def full_recovery_sweep(self) -> Dict[str, Any]:
        """Run a full recovery sweep across videos and agents."""
        video_result = self.recover_stuck_videos()
        agent_result = self.reset_failed_agents()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "videos": video_result,
            "agents": agent_result,
        }
