"""
tests/economy/test_waste_detection.py

Validates Phase 11.4 Failure & Waste Detector.
"""
from app.services.economy.failure_detector import FailureDetector

def test_content_waste():
    fd = FailureDetector()
    signals = fd.evaluate_content(retention_score=15.0, views=50)
    assert "WASTE_SIGNAL" in signals
    assert "LOW_VIEWS" in signals

def test_format_deprecation():
    fd = FailureDetector()
    assert fd.evaluate_format([10.0, 15.0, 20.0]) == "DEPRECATE_FORMAT"
    assert fd.evaluate_format([10.0, 50.0, 60.0]) == "FORMAT_HEALTHY"

def test_channel_death():
    fd = FailureDetector()
    assert fd.evaluate_channel(monthly_growth=-5.0, days_stagnant=35) == "KILL_CHANNEL_SUGGESTION"
    assert fd.evaluate_channel(monthly_growth=10.0, days_stagnant=5) == "CHANNEL_ACTIVE"
