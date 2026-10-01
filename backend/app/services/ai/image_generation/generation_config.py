"""
app/services/ai/image_generation/generation_config.py

Phase SDXL
Configuration settings for SDXL execution.
"""
import os

class SDXLConfig:
    MODEL_ID = os.getenv("SDXL_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
    DEVICE = os.getenv("SDXL_DEVICE", "cuda")
    ENABLE_XFORMERS = os.getenv("SDXL_ENABLE_XFORMERS", "true").lower() == "true"
    ENABLE_CPU_OFFLOAD = os.getenv("SDXL_ENABLE_CPU_OFFLOAD", "true").lower() == "true"
    IMAGE_WIDTH = int(os.getenv("SDXL_IMAGE_WIDTH", "1024"))
    IMAGE_HEIGHT = int(os.getenv("SDXL_IMAGE_HEIGHT", "1024"))
    STEPS = int(os.getenv("SDXL_STEPS", "30"))
    GUIDANCE_SCALE = float(os.getenv("SDXL_GUIDANCE_SCALE", "7.5"))
    CACHE_DIR = os.getenv("SDXL_CACHE_DIR", "media/cache/images")

config = SDXLConfig()
