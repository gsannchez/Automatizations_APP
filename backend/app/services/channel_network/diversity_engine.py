"""
app/services/channel_network/diversity_engine.py

Phase 11.2
Computes channel similarity matrix and enforces diversity thresholds.
"""
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DiversityEngine:
    def compute_similarity_matrix(self, channels_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Computes a heuristic similarity matrix between active channels."""
        matrix = {}
        for c1 in channels_data:
            matrix[c1["id"]] = {}
            for c2 in channels_data:
                if c1["id"] == c2["id"]:
                    matrix[c1["id"]][c2["id"]] = 1.0
                else:
                    # Heuristic: 0.8 if same niche, 0.2 otherwise
                    score = 0.8 if c1.get("niche") == c2.get("niche") else 0.2
                    matrix[c1["id"]][c2["id"]] = score
        return matrix

    def check_diversity_threshold(self, matrix: Dict[str, Dict[str, float]], threshold: float = 0.85) -> List[str]:
        """Returns a list of channel IDs that are too similar and violate the threshold."""
        violations = []
        for c1_id, comparisons in matrix.items():
            for c2_id, score in comparisons.items():
                if c1_id != c2_id and score >= threshold:
                    violations.append(c1_id)
        return list(set(violations))
