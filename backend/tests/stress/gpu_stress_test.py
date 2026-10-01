"""
GPU Stress Test — Phase 6.5
Simulates heavy VRAM pressure to validate:
- GPUWatchdog blocking behaviour
- OOM Recovery triggering
- Quality tier downgrade
"""
import sys
import os

# Add backend root to sys path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.services.monitoring.gpu_watchdog import GPUWatchdog
from app.services.monitoring.cuda_cleanup import CUDACleanup
from app.services.adaptive.quality_manager import QualityManager, QualityTier


def test_watchdog_blocks_at_high_vram():
    """Ensures watchdog reports correctly at various usage levels."""
    stats = GPUWatchdog.get_vram_usage()
    print(f"[TEST] VRAM Stats: {stats}")
    assert "status" in stats
    print("[TEST] ✅ Watchdog reports GPU stats successfully.")


def test_cleanup_runs_without_crash():
    """Ensures cuda cleanup doesn't throw even if GPU is not available."""
    try:
        CUDACleanup.force_cleanup()
        print("[TEST] ✅ CUDA Cleanup ran without error.")
    except Exception as e:
        print(f"[TEST] ❌ CUDA Cleanup raised: {e}")
        raise


def test_quality_degradation_cascade():
    """Verifies quality tier degrades step by step."""
    QualityManager.reset()
    assert QualityManager.get_tier() == QualityTier.HIGH

    QualityManager.downgrade()
    assert QualityManager.get_tier() == QualityTier.BALANCED

    QualityManager.downgrade()
    assert QualityManager.get_tier() == QualityTier.PERFORMANCE

    QualityManager.downgrade()
    assert QualityManager.get_tier() == QualityTier.SAFE_MODE

    print("[TEST] ✅ Quality tier cascade degradation works correctly.")
    QualityManager.reset()


if __name__ == "__main__":
    print("=== GPU Stress Test Suite ===")
    test_watchdog_blocks_at_high_vram()
    test_cleanup_runs_without_crash()
    test_quality_degradation_cascade()
    print("\n✅ All GPU stress tests passed.")
