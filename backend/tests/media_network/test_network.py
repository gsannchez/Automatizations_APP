"""
tests/media_network/test_network.py

Validates the Phase 11 Autonomous AI Media Network modules.
"""
import pytest
from app.services.channel_network.channel_modules import NicheAllocator
from app.services.brand_ai.brand_modules import SloganGenerator
from app.services.universe_engine.universe_manager import UniverseManager
from app.services.publishing_ai.scheduling_modules import PublishingCalendar
from app.services.revenue_ai.revenue_modules import RevenueForecaster
from app.services.prediction_ai.prediction_modules import TrendForecaster

def test_niche_allocator():
    alloc = NicheAllocator()
    existing = [{"niche": "horror"}, {"niche": "gaming"}]
    safe = alloc.allocate_niche("horror", existing)
    assert safe == "horror_hyper_specific"
    
def test_slogan_generator():
    slogan = SloganGenerator().generate("SpookyTV", "horror")
    assert "SpookyTV" in slogan

def test_revenue_forecaster():
    forecaster = RevenueForecaster()
    result = forecaster.forecast("ch1", "finance", 500000)
    assert result["estimated_cpm"] > 10.0
    assert result["sponsorship_ready"] is True

def test_trend_forecaster():
    forecaster = TrendForecaster()
    result = forecaster.forecast("AI Avatars", {"data": 123})
    assert "wave_status" in result
    assert "saturation_score" in result
    
def test_publishing_calendar():
    calendar = PublishingCalendar()
    # Mock planning
    calendar.plan_week("ch1", ["vid1", "vid2"])
