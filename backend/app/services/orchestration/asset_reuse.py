"""Phase 8: Smart Asset Reuse Engine — avoid redundant renders using vector similarity."""
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ...services.autonomous_learning.vector_memory import LightweightVectorMemory

logger = logging.getLogger(__name__)


@dataclass
class ReuseResult:
    reusable: bool
    asset_path: Optional[str]
    similarity_score: float
    reuse_type: str  # "clip" | "audio" | "render" | "none"


class AssetReuseEngine:
    """
    Detects reusable clips, audio, and renders to reduce compute cost.
    Uses the LightweightVectorMemory for semantic scene matching.
    """

    def __init__(self, media_dir: str = "media") -> None:
        self.media_dir = media_dir
        self._scene_memory = LightweightVectorMemory()
        self._audio_memory = LightweightVectorMemory()
        self._asset_index: Dict[str, str] = {}  # text_key -> path

    def index_existing_asset(self, scene_text: str, asset_path: str, asset_type: str = "clip") -> None:
        """Register a rendered asset into the reuse index."""
        key = f"{asset_type}::{scene_text.lower().strip()}"
        self._asset_index[key] = asset_path
        if asset_type == "clip":
            self._scene_memory.add_idea(scene_text)
        elif asset_type == "audio":
            self._audio_memory.add_idea(scene_text)
        logger.debug(f"[AssetReuse] Indexed {asset_type}: '{scene_text[:40]}…' -> {asset_path}")

    def check_reuse(self, scene_text: str, asset_type: str = "clip", threshold: float = 0.85) -> ReuseResult:
        """Check if a close-enough asset exists to avoid re-rendering."""
        mem = self._scene_memory if asset_type == "clip" else self._audio_memory
        sim = mem.check_similarity(scene_text)

        if sim >= threshold:
            # Find the best matching indexed path
            match_path = None
            for key, path in self._asset_index.items():
                if key.startswith(asset_type) and os.path.exists(path):
                    match_path = path
                    break

            if match_path:
                logger.info(f"[AssetReuse] Reusing {asset_type} (sim={sim:.2f}): {match_path}")
                return ReuseResult(reusable=True, asset_path=match_path, similarity_score=sim, reuse_type=asset_type)

        return ReuseResult(reusable=False, asset_path=None, similarity_score=sim, reuse_type="none")

    def check_scenes_batch(self, scenes: List[Dict[str, Any]], threshold: float = 0.85) -> List[ReuseResult]:
        """Check a list of scenes for reusable assets."""
        results = []
        for scene in scenes:
            text = scene.get("voiceover_text", "") or scene.get("description", "")
            results.append(self.check_reuse(text, "clip", threshold))
        return results

    def stats(self) -> Dict[str, Any]:
        return {
            "indexed_assets": len(self._asset_index),
            "scene_memory_size": len(self._scene_memory.memory),
            "audio_memory_size": len(self._audio_memory.memory),
        }
