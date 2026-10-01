"""
tests/economy/test_value_engine.py

Validates the Phase 11.4 Media Value Engine.
"""
from app.services.economy.media_value_engine import MediaValueEngine

def test_value_calculation():
    engine = MediaValueEngine()
    result = engine.calculate_value(100.0, 50.0, 10.0, 5.0)
    assert result["value_score"] > 0
    assert "views_velocity_contribution" in result["breakdown"]

def test_content_value_score():
    engine = MediaValueEngine()
    metrics = {"views_velocity": 200.0, "retention_score": 60.0, "engagement_rate": 15.0, "revenue_estimate": 10.0}
    score = engine.content_value_score(metrics)
    assert score["value_score"] > 50.0
