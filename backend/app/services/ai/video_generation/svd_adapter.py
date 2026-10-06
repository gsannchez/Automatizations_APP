"""Stable Video Diffusion (img2vid) adapter — local GPU, 8-12 GB friendly.

Implements the ``BaseVideoGeneratorAdapter`` contract from
``app.services.video_generator_future`` so it plugs into ``VideoGeneratorFactory``
with zero changes to the pipeline.

VRAM strategy for 8-12 GB:
  * fp16 weights
  * ``enable_model_cpu_offload()`` (weights streamed, only one submodule on GPU)
  * ``unet.enable_forward_chunking()``
  * small ``decode_chunk_size`` (VAE decode is the memory spike)
"""
from __future__ import annotations

import importlib.util
import logging
import os
import tempfile
import time
from typing import Any, Dict

from app.core.config import settings

from .frames_export import frames_to_mp4

from ...video_generator_future import (
    AIVideoBackend,
    BaseVideoGeneratorAdapter,
    GenerationMode,
    VideoGenerationRequest,
    VideoGenerationResult,
)

logger = logging.getLogger(__name__)

# SVD is trained at 1024x576 landscape; portrait 576x1024 works for 9:16.
PORTRAIT_WIDTH = 576
PORTRAIT_HEIGHT = 1024


def _fit_cover(image, width: int, height: int):
    """Scale *image* to cover ``width x height`` then centre-crop it.

    A plain ``resize`` would stretch the input whenever its aspect ratio differs
    from 9:16; covering and cropping preserves the composition instead.
    """
    from PIL import Image

    src_w, src_h = image.size
    scale = max(width / src_w, height / src_h)
    scaled = (
        max(int(round(src_w * scale)), width),
        max(int(round(src_h * scale)), height),
    )
    image = image.resize(scaled, Image.LANCZOS)

    left = (scaled[0] - width) // 2
    top = (scaled[1] - height) // 2
    return image.crop((left, top, left + width, top + height))


class SVDAdapter(BaseVideoGeneratorAdapter):
    backend_id = AIVideoBackend.SVD
    min_vram_gb = 8.0
    supports_modes = [GenerationMode.IMAGE_TO_VIDEO]

    def __init__(self) -> None:
        self.model_id = settings.SVD_MODEL_ID
        self._pipe = None

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------
    def is_available(self) -> bool:
        try:
            import torch  # noqa: F401

            if not torch.cuda.is_available():
                return False
            if importlib.util.find_spec("diffusers") is None:
                return False
            return True
        except Exception as exc:  # pragma: no cover - env dependent
            logger.debug("SVD not available: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Pipeline lifecycle
    # ------------------------------------------------------------------
    def _load_pipeline(self):
        if self._pipe is not None:
            return self._pipe

        import torch
        from diffusers import StableVideoDiffusionPipeline

        load_kwargs: Dict[str, Any] = {"torch_dtype": torch.float16, "variant": "fp16"}
        if settings.HF_TOKEN:
            load_kwargs["token"] = settings.HF_TOKEN

        logger.info("Loading SVD pipeline %s (first run downloads ~9.5 GB)", self.model_id)
        pipe = StableVideoDiffusionPipeline.from_pretrained(self.model_id, **load_kwargs)

        if settings.SVD_CPU_OFFLOAD and hasattr(pipe, "enable_model_cpu_offload"):
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cuda")

        if hasattr(pipe.unet, "enable_forward_chunking"):
            pipe.unet.enable_forward_chunking()

        self._pipe = pipe
        return pipe

    def release(self) -> None:
        """Drop the pipeline and free VRAM (call between videos)."""
        self._pipe = None
        try:
            import torch

            torch.cuda.empty_cache()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------
    def generate(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        start = time.time()

        if not request.input_image_path or not os.path.exists(request.input_image_path):
            return VideoGenerationResult(
                success=False,
                backend_used=self.backend_id.value,
                error="SVD requires an existing input_image_path (img2vid).",
            )

        try:
            import torch
            from PIL import Image

            pipe = self._load_pipeline()

            image = Image.open(request.input_image_path).convert("RGB")
            image = _fit_cover(image, PORTRAIT_WIDTH, PORTRAIT_HEIGHT)

            generator = torch.manual_seed(request.seed or 42)
            num_frames = settings.SVD_NUM_FRAMES

            result = pipe(
                image,
                decode_chunk_size=settings.SVD_DECODE_CHUNK_SIZE,
                num_frames=num_frames,
                height=PORTRAIT_HEIGHT,
                width=PORTRAIT_WIDTH,
                fps=settings.SVD_FPS,
                motion_bucket_id=127,
                generator=generator,
            )
            frames = result.frames[0]

            fd, out_path = tempfile.mkstemp(suffix=".mp4", prefix="svd_scene_")
            os.close(fd)
            frames_to_mp4(frames, out_path, fps=settings.SVD_FPS)

            del result, frames
            torch.cuda.empty_cache()

            return VideoGenerationResult(
                success=True,
                output_path=out_path,
                backend_used=self.backend_id.value,
                duration_seconds=num_frames / float(settings.SVD_FPS),
                generation_time_seconds=time.time() - start,
                metadata={
                    "model_id": self.model_id,
                    "num_frames": num_frames,
                    "fps": settings.SVD_FPS,
                    "width": PORTRAIT_WIDTH,
                    "height": PORTRAIT_HEIGHT,
                },
            )

        except Exception as exc:  # pragma: no cover - GPU/env dependent
            logger.error("SVD generation failed: %s", exc, exc_info=True)
            try:
                import torch

                torch.cuda.empty_cache()
            except Exception:
                pass
            return VideoGenerationResult(
                success=False,
                backend_used=self.backend_id.value,
                error=str(exc),
            )

    def get_backend_info(self) -> Dict[str, Any]:
        return {
            "backend": self.backend_id.value,
            "status": "ready" if self.is_available() else "unavailable",
            "min_vram_gb": self.min_vram_gb,
            "model_id": self.model_id,
            "description": "Stable Video Diffusion XT 1.1 — img2vid, portrait 576x1024 @7fps.",
        }
