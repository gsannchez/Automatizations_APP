"""Engagement Analyzer — per-scene drop-off analysis and engagement scoring.

Identifies scenes causing viewer drop-off using retention curve data.
Works with VideoPerformanceMetrics.retention_data JSONB field.
"""
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class EngagementAnalyzer:
    """Analyzes retention curves and computes scene-level engagement scores.

    Takes a retention_data dictionary (time_seconds → retention_percentage)
    and identifies drop-off hotspots, strong engagement peaks, and provides
    actionable per-scene insights.
    """

    # Thresholds for classification
    DROP_THRESHOLD = 10.0   # % drop in 5s → drop-off event
    PEAK_THRESHOLD = 5.0    # % gain → engagement peak (replay/rewatch)

    def analyze_retention_curve(
        self, retention_data: Dict[str, float], video_duration: float
    ) -> Dict[str, Any]:
        """Analyze a retention curve and return engagement insights.

        Args:
            retention_data: Dict mapping time keys (str seconds) to retention %.
            video_duration: Total video duration in seconds.

        Returns:
            Dict with drop-off events, peak moments, average retention, and grade.
        """
        if not retention_data:
            logger.warning("Empty retention data — returning default analysis.")
            return self._empty_result()

        # Sort data points chronologically
        timeline: List[Tuple[float, float]] = sorted(
            [(float(k), float(v)) for k, v in retention_data.items()],
            key=lambda x: x[0],
        )

        drop_off_events: List[Dict[str, Any]] = []
        peak_moments: List[Dict[str, Any]] = []
        retention_values = [v for _, v in timeline]

        for i in range(1, len(timeline)):
            prev_t, prev_r = timeline[i - 1]
            curr_t, curr_r = timeline[i]
            delta = curr_r - prev_r

            if delta <= -self.DROP_THRESHOLD:
                drop_off_events.append({
                    "time_start": prev_t,
                    "time_end": curr_t,
                    "retention_drop": abs(delta),
                    "severity": "critical" if abs(delta) >= 20 else "moderate",
                    "recommendation": self._drop_recommendation(prev_t, video_duration),
                })
            elif delta >= self.PEAK_THRESHOLD:
                peak_moments.append({
                    "time": curr_t,
                    "retention_gain": delta,
                    "note": "Rewatch or spike — strong content moment",
                })

        avg_retention = sum(retention_values) / len(retention_values) if retention_values else 0.0
        hook_retention = retention_values[0] if retention_values else 100.0  # First point
        final_retention = retention_values[-1] if retention_values else 0.0

        grade = self._grade_retention(avg_retention, hook_retention, final_retention)

        logger.info(
            f"Engagement analysis complete: avg_retention={avg_retention:.1f}%, "
            f"drops={len(drop_off_events)}, peaks={len(peak_moments)}, grade={grade}"
        )

        return {
            "average_retention": round(avg_retention, 2),
            "hook_retention": round(hook_retention, 2),
            "final_retention": round(final_retention, 2),
            "drop_off_count": len(drop_off_events),
            "drop_off_events": drop_off_events,
            "peak_moments": peak_moments,
            "engagement_grade": grade,
            "total_data_points": len(timeline),
        }

    def _drop_recommendation(self, time_seconds: float, duration: float) -> str:
        """Generate context-aware drop-off fix recommendation based on position."""
        position_ratio = time_seconds / max(duration, 1.0)
        if position_ratio < 0.15:
            return (
                "Drop-off en los primeros segundos. El gancho no está funcionando. "
                "Reescribe la primera frase con tensión inmediata."
            )
        elif position_ratio < 0.50:
            return (
                "Drop-off en la sección media. Añade un giro narrativo o un nuevo dato "
                "sorprendente aquí para reactivar la atención."
            )
        else:
            return (
                "Drop-off cerca del final. Añade un CTA o cliffhanger antes de que el "
                "espectador decida marcharse."
            )

    def _grade_retention(
        self, avg: float, hook: float, final: float
    ) -> str:
        """Assign an A-F grade based on retention metrics."""
        if avg >= 65 and hook >= 85 and final >= 40:
            return "A"
        elif avg >= 50 and hook >= 70:
            return "B"
        elif avg >= 35 and hook >= 55:
            return "C"
        elif avg >= 20:
            return "D"
        else:
            return "F"

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "average_retention": 0.0,
            "hook_retention": 0.0,
            "final_retention": 0.0,
            "drop_off_count": 0,
            "drop_off_events": [],
            "peak_moments": [],
            "engagement_grade": "N/A",
            "total_data_points": 0,
        }

    def scene_engagement_map(
        self,
        retention_data: Dict[str, float],
        scene_timestamps: List[Tuple[float, float]],
    ) -> List[Dict[str, Any]]:
        """Map retention data to specific scenes for targeted optimization.

        Args:
            retention_data: Dict of time→retention%.
            scene_timestamps: List of (start_sec, end_sec) tuples per scene.

        Returns:
            List of scene dicts with engagement score and status.
        """
        results = []
        for idx, (start, end) in enumerate(scene_timestamps):
            # Collect retention points within scene window
            points = [
                v for k, v in retention_data.items()
                if start <= float(k) <= end
            ]
            avg = sum(points) / len(points) if points else 50.0

            status = "strong" if avg >= 60 else "weak" if avg < 35 else "average"
            results.append({
                "scene_index": idx,
                "start_time": start,
                "end_time": end,
                "avg_retention": round(avg, 2),
                "status": status,
            })

        return results
