"""Phase 8: Resource-Aware Task Planner — heuristic system health monitor."""
import logging
import os
import shutil
from dataclasses import dataclass
from typing import Dict, Any

logger = logging.getLogger(__name__)

SAFE_MODE_ENV = "SAFE_MODE"
VRAM_THRESHOLD_MB = int(os.getenv("VRAM_THRESHOLD_MB", "2048"))
RAM_THRESHOLD_PCT = float(os.getenv("RAM_THRESHOLD_PCT", "85.0"))
DISK_THRESHOLD_PCT = float(os.getenv("DISK_THRESHOLD_PCT", "90.0"))


@dataclass
class SystemHealth:
    cpu_pct: float
    ram_pct: float
    disk_pct: float
    safe_mode: bool
    ai_video_allowed: bool
    render_tier: str   # "high" | "medium" | "low"
    recommendation: str


class ResourcePlanner:
    """
    Reads lightweight system metrics via stdlib and applies heuristic thresholds.
    No psutil dependency; uses shutil and os fallbacks for maximum portability.
    """

    @staticmethod
    def _disk_usage_pct(path: str = ".") -> float:
        try:
            total, used, free = shutil.disk_usage(path)
            return (used / total) * 100.0
        except Exception:
            return 0.0

    @staticmethod
    def _ram_pct() -> float:
        """Best-effort RAM usage. Falls back to 0 if psutil unavailable."""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0

    @staticmethod
    def _cpu_pct() -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0

    def evaluate(self) -> SystemHealth:
        cpu = self._cpu_pct()
        ram = self._ram_pct()
        disk = self._disk_usage_pct()
        safe_mode_env = os.getenv(SAFE_MODE_ENV, "false").lower() == "true"

        overloaded = ram > RAM_THRESHOLD_PCT or disk > DISK_THRESHOLD_PCT or safe_mode_env

        if overloaded:
            render_tier = "low"
            ai_video_allowed = False
            recommendation = "System under pressure. Delaying heavy renders, AI video disabled."
        elif ram > 70.0 or cpu > 80.0:
            render_tier = "medium"
            ai_video_allowed = True
            recommendation = "Moderate load. Using medium render tier."
        else:
            render_tier = "high"
            ai_video_allowed = True
            recommendation = "System healthy. Full render tier active."

        health = SystemHealth(
            cpu_pct=cpu,
            ram_pct=ram,
            disk_pct=disk,
            safe_mode=overloaded,
            ai_video_allowed=ai_video_allowed,
            render_tier=render_tier,
            recommendation=recommendation,
        )
        logger.info(f"[ResourcePlanner] cpu={cpu:.1f}% ram={ram:.1f}% disk={disk:.1f}% tier={render_tier}")
        return health

    def to_dict(self) -> Dict[str, Any]:
        h = self.evaluate()
        return {
            "cpu_pct": h.cpu_pct,
            "ram_pct": h.ram_pct,
            "disk_pct": h.disk_pct,
            "safe_mode": h.safe_mode,
            "ai_video_allowed": h.ai_video_allowed,
            "render_tier": h.render_tier,
            "recommendation": h.recommendation,
        }
