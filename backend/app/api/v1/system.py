from fastapi import APIRouter
from ...services.health.pipeline_health import PipelineHealth
from ...services.monitoring.gpu_watchdog import GPUWatchdog
from ...services.comfyui_health import get_comfyui_status

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
def system_health():
    """Returns overall pipeline health status."""
    return PipelineHealth.get_status()

@router.get("/gpu")
def gpu_status():
    """Returns real-time VRAM and GPU metrics."""
    return GPUWatchdog.get_vram_usage()

@router.get("/comfyui")
def comfyui_status():
    """ComfyUI reachability and configuration."""
    return get_comfyui_status()


@router.get("/pipeline-status")
def pipeline_status():
    """Returns full pipeline diagnostics."""
    return {
        "pipeline": PipelineHealth.get_status(),
        "gpu": GPUWatchdog.get_vram_usage(),
        "comfyui": get_comfyui_status(),
    }

