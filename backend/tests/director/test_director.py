"""
tests/director/test_director.py

Validates the Phase 10 AI Director modules.
"""
import pytest
from app.services.quality_ai.scene_quality_analyzer import SceneQualityAnalyzer
from app.services.pacing_ai.scene_duration_optimizer import SceneDurationOptimizer
from app.services.regeneration.regeneration_manager import RegenerationManager
from app.services.consistency.scene_transition_manager import SceneTransitionManager
from app.services.variants.battle_engine import BattleEngine

@pytest.mark.asyncio
async def test_scene_quality_analyzer():
    analyzer = SceneQualityAnalyzer()
    # Using mock deterministic paths
    result = await analyzer.evaluate_video("mock_bad_video.mp4")
    assert "score" in result
    assert "metrics" in result
    assert isinstance(result["regeneration_recommended"], bool)

def test_pacing_optimizer():
    optimizer = SceneDurationOptimizer()
    scenes = [
        {"duration": 4.0},
        {"duration": 6.0}, # Too long
        {"duration": 2.0}
    ]
    result = optimizer.optimize_pacing(scenes)
    opt_scenes = result["optimized_scenes"]
    
    # Hook reinforcer should trim the first scene if > 3s
    assert opt_scenes[0]["duration"] <= 3.0
    # Middle scene > 5.0 should be trimmed
    assert opt_scenes[1]["duration"] <= 5.0

def test_scene_transition_manager():
    manager = SceneTransitionManager()
    result = manager.evaluate_continuity([{"scene": 1}])
    assert "continuity_score" in result
    assert "visual_drift_alerts" in result
