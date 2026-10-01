"""
app/services/economy/global_performance_index.py

Phase 11.4
Computes Global Performance Index (GPI) for the entire media company.
"""
from typing import Dict, Any

class GlobalPerformanceIndex:
    def calculate_gpi(self, avg_retention: float, total_growth: float, revenue_projection: float, diversity_score: float) -> Dict[str, Any]:
        """Formula for GPI."""
        gpi = (avg_retention * 0.4) + (total_growth * 0.3) + (revenue_projection * 0.2) + (diversity_score * 0.1)
        return {
            "gpi": float(gpi),
            "breakdown": {
                "retention_impact": float(avg_retention * 0.4),
                "growth_impact": float(total_growth * 0.3),
                "revenue_impact": float(revenue_projection * 0.2),
                "diversity_impact": float(diversity_score * 0.1)
            }
        }
