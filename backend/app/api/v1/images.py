"""
app/api/v1/images.py

Phase SDXL
Endpoints for manual SDXL generation and health checks.
"""
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from app.services.ai.image_generation.sdxl_generator import SDXLGenerator
from app.services.ai.image_generation.model_manager import model_manager
from app.services.ai.image_generation.gpu_image_guard import GPUImageGuard

router = APIRouter(prefix="/images", tags=["Images"])

class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    style: str = "CINEMATIC"
    seed: Optional[int] = None

@router.post("/generate")
async def generate_image(req: ImageRequest):
    try:
        generator = SDXLGenerator()
        path = await generator.generate_image(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt,
            width=req.width,
            height=req.height,
            style=req.style,
            seed=req.seed
        )
        return {"status": "success", "image_path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health():
    guard = GPUImageGuard()
    return {
        "status": "online",
        "vram_usage_percent": guard.get_vram_usage_percent(),
        "model_loaded": model_manager._pipeline is not None
    }

@router.post("/warmup")
async def warmup_model(background_tasks: BackgroundTasks):
    background_tasks.add_task(model_manager.warmup)
    return {"status": "warmup_started"}
