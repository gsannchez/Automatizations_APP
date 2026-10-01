"""
tests/media_network/test_universe_engine.py

Validates the Phase 11.3 Universe Expansion Engine logic.
"""
import pytest
from app.services.universe_engine.universe_expansion import UniverseExpansionEngine
from app.services.universe_engine.story_arc_engine import StoryArcEngine
from app.services.universe_engine.character_memory import CharacterMemory
from app.services.universe_engine.character_evolution import CharacterEvolutionEngine
from app.services.universe_engine.lore_tracker import LoreTracker
from app.services.universe_engine.lore_compressor import LoreCompressor
from app.services.universe_engine.universe_linker import UniverseLinker

def test_universe_expansion():
    ue = UniverseExpansionEngine()
    assert ue.evaluate_expansion({"is_retcon": True}, []) is False
    assert ue.evaluate_expansion({"is_retcon": False}, []) is True

def test_story_arc_engine():
    engine = StoryArcEngine()
    arc = engine.start_arc("uni_1", "The Beginning")
    assert arc["stage"] == "INTRO"
    
    advanced = engine.progress_arc(arc)
    assert advanced["stage"] == "DEVELOPMENT"
    
    with pytest.raises(ValueError):
        engine.start_arc("uni_1", "Another Dominant Arc", is_dominant=True)

def test_character_consistency():
    mem = CharacterMemory()
    mem.track_recurring({"id": "char_1", "emotional_profile": {"baseline": "stoic"}})
    assert mem.maintain_emotional_continuity("char_1", "hysterical") is False
    assert mem.maintain_emotional_continuity("char_1", "calm") is True

def test_character_evolution():
    ev = CharacterEvolutionEngine()
    char = {}
    evolved = ev.evolve_character(char, trigger_event="Trauma", arc_transition=False)
    assert len(evolved["evolution_log"]) == 1
    
    with pytest.raises(ValueError):
        ev.evolve_character(char, trigger_event="", arc_transition=False)

def test_lore_tracker_and_compressor():
    tracker = LoreTracker()
    hierarchy = {
        "arc_1": {
            "scene_1": ["John is alive"]
        }
    }
    assert tracker.prevent_contradictions("John died", hierarchy) is False
    assert tracker.prevent_contradictions("John found a sword", hierarchy) is True
    
    compressor = LoreCompressor()
    compressed = compressor.compress_lore(["Event 1", "Event 2"])
    assert "2" in compressed

def test_universe_linker():
    linker = UniverseLinker()
    crossover = linker.create_crossover("uni_A", "uni_B", "Sci-Fi Magic")
    assert crossover["status"] == "pending_orchestrator_approval"
    
    with pytest.raises(ValueError):
        linker.create_crossover("uni_A", "uni_B", "")
