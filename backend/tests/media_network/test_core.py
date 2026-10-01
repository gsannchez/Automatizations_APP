"""
tests/media_network/test_core.py

Validates the Phase 11.1 Autonomous AI Media Network core functionality.
"""
from app.services.channel_network.niche_allocator import NicheAllocator
from app.services.brand_ai.slogan_generator import SloganGenerator
from app.services.universe_engine.lore_tracker import LoreTracker
from app.services.publishing_ai.schedule_optimizer import ScheduleOptimizer
from app.services.channel_network.cross_channel_learning import CrossChannelLearning

def test_niche_overlap_prevention():
    alloc = NicheAllocator()
    existing = ["horror", "gaming"]
    safe = alloc.allocate_niche("horror", existing)
    assert safe == "horror_hyper_niche"
    safe2 = alloc.allocate_niche("finance", existing)
    assert safe2 == "finance"

def test_continuity_conflict_detection():
    tracker = LoreTracker()
    assert tracker.prevent_contradictions("new lore", ["old lore"]) is True

def test_publishing_cadence_validation():
    opt = ScheduleOptimizer()
    assert "18:00" in opt.determine_ideal_windows("gen_z")
    assert opt.avoid_overposting("ch1", "12:00", []) is True

def test_cross_channel_learning_safety():
    learner = CrossChannelLearning()
    assert learner.check_duplication("hook1", ["hook1", "hook2"]) is True
    assert learner.calculate_diversity_score(["h1", "h2", "h3"]) == 100.0
    assert learner.calculate_diversity_score(["h1", "h1", "h2"]) < 100.0

def test_channel_growth_scoring():
    # Placeholder for channel growth score logic
    assert True
