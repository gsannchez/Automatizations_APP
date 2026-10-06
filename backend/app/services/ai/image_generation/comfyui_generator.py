"""
app/services/ai/image_generation/comfyui_generator.py

ComfyUI integration for image generation.
"""
import os
import time
import httpx
import asyncio
import logging
from typing import Optional
from pathlib import Path

from app.core.config import settings
from app.services.ai.base.base_image_generator import BaseImageGenerator
from .image_cache import ImageCache

logger = logging.getLogger(__name__)

# Single source of truth: settings (which itself reads the .env / environment).
DEFAULT_CHECKPOINT = settings.COMFYUI_CHECKPOINT


class ComfyUIGenerator(BaseImageGenerator):
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.COMFYUI_URL).rstrip("/")
        self.cache = ImageCache()
        self.checkpoint_name = DEFAULT_CHECKPOINT

    def _create_workflow(self, prompt: str, negative_prompt: str, width: int = 896, height: int = 1152, seed: int = 42):
        """Creates the JSON workflow for ComfyUI using Juggernaut XL v9.
        Using 896x1152 by default as it's a good 9:16 approx for SDXL."""
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": 7,
                    "denoise": 1,
                    "latent_image": ["5", 0],
                    "model": ["4", 0],
                    "negative": ["7", 0],
                    "positive": ["6", 0],
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "seed": seed,
                    "steps": 25
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": self.checkpoint_name
                }
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"batch_size": 1, "height": height, "width": width}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["4", 1], "text": prompt}
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["4", 1], "text": negative_prompt}
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]}
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "output", "images": ["8", 0]}
            }
        }

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        style: str,
        seed: Optional[int] = None,
        latent_reuse_params: Optional[dict] = None,
        output_path: Optional[str] = None,
        max_wait_seconds: int = 90,
    ) -> str:
        effective_prompt = prompt
        if latent_reuse_params and latent_reuse_params.get("use_freeu"):
            effective_prompt = f"{prompt}, latent temporal consistency, stable motion, no flicker"

        logger.info(f"[ComfyUI] Generating image for prompt: {effective_prompt[:30]}...")
        
        # 1. Check cache
        cached_path = self.cache.get_cached_image(effective_prompt, style, seed)
        if cached_path:
            logger.info(f"[ComfyUI] Found in cache: {cached_path}")
            return cached_path
            
        target_path = output_path or self.cache.get_cache_path(effective_prompt, style, seed)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Default seed if not provided
        gen_seed = seed if seed is not None else int(time.time())
        
        # 2. Free VRAM and clear stale queue so new prompts are not stuck behind zombies
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                await client.post(f"{self.base_url}/free", json={"unload_models": False, "free_memory": True})
            except Exception:
                pass  # non-critical
            try:
                q_res = await client.get(f"{self.base_url}/queue")
                q_res.raise_for_status()
                q_data = q_res.json()
                running = q_data.get("queue_running") or []
                pending = q_data.get("queue_pending") or []
                if running or pending:
                    logger.warning(
                        "[ComfyUI] Clearing queue before generate (%d running, %d pending)",
                        len(running),
                        len(pending),
                    )
                    await client.post(f"{self.base_url}/interrupt")
                    await client.post(f"{self.base_url}/queue", json={"clear": True})
            except Exception as exc:
                logger.warning("[ComfyUI] Queue clear skipped: %s", exc)

        # 3. Build workflow
        workflow = self._create_workflow(effective_prompt, negative_prompt, width, height, gen_seed)
        
        # 4. Request generation
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(f"{self.base_url}/prompt", json={"prompt": workflow})
                response.raise_for_status()
                prompt_id = response.json().get("prompt_id")
            except Exception as e:
                logger.error(f"[ComfyUI] Error queuing prompt: {e}")
                raise RuntimeError(f"Failed to queue prompt in ComfyUI: {e}")

        logger.info("[ComfyUI] Queued prompt %s, waiting up to %ss", prompt_id, max_wait_seconds)

        # 5. Poll history until completion (bounded wait)
        deadline = time.monotonic() + max_wait_seconds
        async with httpx.AsyncClient(timeout=30.0) as client:
            history_data = {}
            while time.monotonic() < deadline:
                try:
                    history_res = await client.get(f"{self.base_url}/history/{prompt_id}")
                    history_res.raise_for_status()
                    history_data = history_res.json()
                    if prompt_id in history_data:
                        break
                except httpx.RequestError as e:
                    logger.warning("[ComfyUI] Polling error: %s", e)
                await asyncio.sleep(2)
            else:
                queue_hint = ""
                try:
                    q_res = await client.get(f"{self.base_url}/queue")
                    q_data = q_res.json()
                    running = [item[1] for item in q_data.get("queue_running", []) if len(item) > 1]
                    pending = [item[1] for item in q_data.get("queue_pending", []) if len(item) > 1]
                    if prompt_id in pending:
                        queue_hint = (
                            f" Prompt still pending (running={running}, pending={len(pending)}). "
                            "Reinicia ComfyUI si hay un job atascado en 'running'."
                        )
                    elif running:
                        queue_hint = f" ComfyUI busy (running={running})."
                except Exception:
                    pass
                raise TimeoutError(
                    f"ComfyUI did not finish within {max_wait_seconds}s "
                    f"(prompt_id={prompt_id}).{queue_hint}"
                )
            
            # 6. Check for execution errors
            entry = history_data[prompt_id]
            status_info = entry.get("status", {})
            if status_info.get("status_str") == "error":
                messages = status_info.get("messages", [])
                error_detail = "Unknown error"
                for msg in messages:
                    if isinstance(msg, list) and msg[0] == "execution_error":
                        error_detail = msg[1].get("exception_message", error_detail)
                        break
                raise RuntimeError(f"ComfyUI execution failed: {error_detail}")

            # 7. Extract filename from outputs
            outputs = entry.get("outputs", {})
            # Find the SaveImage node output (try node "9" first, then scan all)
            image_output = None
            if "9" in outputs and "images" in outputs["9"]:
                image_output = outputs["9"]["images"][0]
            else:
                for node_id, node_out in outputs.items():
                    if "images" in node_out and node_out["images"]:
                        image_output = node_out["images"][0]
                        break

            if not image_output:
                raise RuntimeError(f"ComfyUI produced no image output for prompt {prompt_id}")
                 
            filename = image_output["filename"]
            
            # 8. Download image
            img_res = await client.get(f"{self.base_url}/view", params={"filename": filename})
            img_res.raise_for_status()
            
            with open(target_path, "wb") as f:
                f.write(img_res.content)
                
            logger.info(f"[ComfyUI] Image successfully saved to {target_path}")
            return target_path

