"""
tests/economy/test_allocation_logic.py

Validates Phase 11.4 Resource Allocation Engine.
"""
from app.services.economy.resource_allocator import ResourceAllocator

def test_gpu_priority():
    alloc = ResourceAllocator()
    channels = [
        {"id": "ch1", "value_score": 100.0, "growth_rate": 50.0},
        {"id": "ch2", "value_score": 10.0, "growth_rate": 5.0}
    ]
    priorities = alloc.allocate_gpu_priority(channels)
    assert priorities["ch1"] > priorities["ch2"]
    assert sum(priorities.values()) == 1.0

def test_campaign_order():
    alloc = ResourceAllocator()
    campaigns = [
        {"id": "c1", "value_score": 10.0, "growth_rate": 0.0},
        {"id": "c2", "value_score": 100.0, "growth_rate": 100.0}
    ]
    sorted_c = alloc.sort_campaign_execution_order(campaigns)
    assert sorted_c[0]["id"] == "c2"
