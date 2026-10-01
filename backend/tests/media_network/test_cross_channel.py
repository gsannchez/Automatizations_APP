"""
tests/media_network/test_cross_channel.py

Validates the Phase 11.2 Cross-Channel Intelligence and Containment logic.
"""
import pytest
from app.services.channel_network.cross_channel_intelligence import CrossChannelIntelligence
from app.services.channel_network.contamination_guard import ContaminationGuard
from app.services.channel_network.pattern_propagator import PatternPropagator
from app.services.channel_network.diversity_engine import DiversityEngine

def test_pattern_extraction():
    cci = CrossChannelIntelligence()
    metrics = [{"channel_id": "ch1", "views": 150000, "format": "listicle"}]
    patterns = cci.detect_viral_patterns(metrics)
    assert len(patterns) == 1
    assert patterns[0]["base_format"] == "listicle"

def test_contamination_guard():
    cg = ContaminationGuard()
    # String heuristic
    assert cg.detect_duplicate_hooks("Watch this crazy thing", ["Watch this crazy thing and more!"]) is True
    assert cg.detect_duplicate_hooks("A completely new hook", ["Watch this crazy thing and more!"]) is False
    
    # Overlapping arcs
    assert cg.detect_overlapping_arcs("ArcA", ["ArcB", "ArcA"]) is True

def test_pattern_adaptation():
    pp = PatternPropagator()
    adapted = pp.adapt_pattern("shock_hook", "finance")
    assert "finance" in adapted
    
    format_spec = {"duration": 60}
    transformed = pp.transform_format(format_spec)
    assert transformed["is_adapted"] is True

def test_diversity_engine():
    de = DiversityEngine()
    channels = [
        {"id": "ch1", "niche": "finance"},
        {"id": "ch2", "niche": "finance"},
        {"id": "ch3", "niche": "gaming"}
    ]
    matrix = de.compute_similarity_matrix(channels)
    assert matrix["ch1"]["ch2"] == 0.8
    assert matrix["ch1"]["ch3"] == 0.2
    
    violations = de.check_diversity_threshold(matrix, threshold=0.75)
    assert "ch1" in violations
    assert "ch3" not in violations
