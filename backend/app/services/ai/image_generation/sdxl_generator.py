"""
app/services/ai/image_generation/sdxl_generator.py

Phase SDXL
Main generator combining model manager, cache, enhancement, and validation.
"""
import logging
import asyncio
import torch
import time
import uuid
from typing import Optional

from app.services.ai.base.base_image_generator import BaseImageGenerator
from .model_manager import model_manager
from .prompt_enhancer import PromptEnhancer
from .image_cache import ImageCache
from .image_quality import ImageQualityValidator
from .gpu_image_guard import GPUImageGuard
from .generation_config import config

logger = logging.getLogger(__name__)

class SDXLGenerator(BaseImageGenerator):
    def __init__(self):
        self.enhancer = PromptEnhancer()
        self.cache = ImageCache()
        self.validator = ImageQualityValidator()
        self.gpu_guard = GPUImageGuard()

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        style: str,
        seed: Optional[int] = None,
        output_path: Optional[str] = None
    ) -> str:
        trace_id = str(uuid.uuid4())[:8]
        logger.info(f"[{trace_id}] Starting SDXL generation | Prompt: {prompt[:30]}... | Style: {style}")
        
        # 1. Check cache
        cached_path = self.cache.get_cached_image(prompt, style, seed)
        if cached_path:
            return cached_path
            
        target_path = output_path or self.cache.get_cache_path(prompt, style, seed)

        # 2. Enhance prompts
        enhanced_prompt = self.enhancer.enhance(prompt, style)
        final_negative = self.enhancer.get_negative_prompt(negative_prompt)
        
        # 3. Guard VRAM
        if not self.gpu_guard.wait_for_vram():
            raise RuntimeError(f"[{trace_id}] VRAM timeout. Cannot safely generate image.")

        vram_before = self.gpu_guard.get_vram_usage_percent()

        # 4. Execute (run in executor to avoid blocking asyncio loop)
        loop = asyncio.get_running_loop()
        start_time = time.time()
        
        try:
            await loop.run_in_executor(
                None, 
                self._run_inference_sync, 
                enhanced_prompt, 
                final_negative, 
                width, 
                height, 
                seed, 
                target_path
            )
        except Exception as e:
            model_manager.cleanup_memory()
            raise RuntimeError(f"[{trace_id}] Generation failed: {str(e)}")
            
        gen_time = time.time() - start_time
        vram_after = self.gpu_guard.get_vram_usage_percent()
        logger.info(f"[{trace_id}] Generation complete in {gen_time:.1f}s. VRAM: {vram_before:.1f}% -> {vram_after:.1f}%")

        # 5. Validate output
        if not self.validator.validate_image(target_path):
            raise RuntimeError(f"[{trace_id}] Validation failed for generated image.")

        # 6. Cleanup
        model_manager.cleanup_memory()
        
        return target_path

    def _run_inference_sync(self, prompt: str, negative_prompt: str, width: int, height: int, seed: Optional[int], target_path: str):
        pipeline = model_manager.get_pipeline()
        
        generator = None
        if seed is not None:
            generator = torch.Generator(device=config.DEVICE).manual_seed(seed)
            
        result = pipeline(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=config.STEPS,
            guidance_scale=config.GUIDANCE_SCALE,
            generator=generator
        )
        
        image = result.images[0]
        image.save(target_path)
