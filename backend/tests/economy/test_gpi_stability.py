"""
tests/economy/test_gpi_stability.py

Validates Phase 11.4 Global Performance Index.
"""
from app.services.economy.global_performance_index import GlobalPerformanceIndex

def test_gpi_calculation():
    gpi = GlobalPerformanceIndex()
    result = gpi.calculate_gpi(avg_retention=50.0, total_growth=100.0, revenue_projection=500.0, diversity_score=1.0)
    
    assert result["gpi"] > 0
    assert result["breakdown"]["retention_impact"] == 20.0 # 50.0 * 0.4
    assert result["breakdown"]["growth_impact"] == 30.0 # 100.0 * 0.3
