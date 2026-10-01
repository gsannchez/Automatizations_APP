"""
app/services/ai/image_generation/model_manager.py

Phase SDXL
Maintains a single global instance of the SDXL pipeline to avoid reloading.
"""
import logging
import gc
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

from .generation_config import config

logger = logging.getLogger(__name__)

class SDXLModelManager:
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SDXLModelManager, cls).__new__(cls)
        return cls._instance

    def load_pipeline(self):
        """Loads the SDXL pipeline with optimal settings for 12GB VRAM."""
        if self._pipeline is not None:
            return

        logger.info(f"Loading SDXL Model: {config.MODEL_ID} on {config.DEVICE}")
        
        try:
            self._pipeline = StableDiffusionXLPipeline.from_pretrained(
                config.MODEL_ID,
                torch_dtype=torch.float16,
                use_safetensors=True,
                variant="fp16"
            )

            # Optimizations for 12GB VRAM
            self._pipeline.scheduler = DPMSolverMultistepScheduler.from_config(self._pipeline.scheduler.config)
            
            if config.ENABLE_XFORMERS:
                self._pipeline.enable_xformers_memory_efficient_attention()
                
            self._pipeline.enable_vae_slicing()
            
            # Slicing attention helps VRAM but is slower. Required for 12GB if using offload.
            # self._pipeline.enable_attention_slicing()
            
            if config.ENABLE_CPU_OFFLOAD:
                self._pipeline.enable_model_cpu_offload()
            else:
                self._pipeline.to(config.DEVICE)
                
            logger.info("SDXL Pipeline loaded successfully.")
            
        except Exception as e:
            logger.error(f"Failed to load SDXL pipeline: {str(e)}")
            self._pipeline = None
            raise

    def get_pipeline(self):
        """Returns the loaded pipeline instance."""
        if self._pipeline is None:
            self.load_pipeline()
        return self._pipeline

    def unload_pipeline(self):
        """Unloads the pipeline to free memory."""
        if self._pipeline is not None:
            del self._pipeline
            self._pipeline = None
            self.cleanup_memory()
            logger.info("SDXL Pipeline unloaded.")

    def cleanup_memory(self):
        """Forces garbage collection and empties CUDA cache."""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def warmup(self):
        """Runs a dummy generation to initialize CUDA graphs/kernels."""
        if self._pipeline is None:
            self.load_pipeline()
        logger.info("Running SDXL warmup...")
        _ = self._pipeline(prompt="a tiny red cube", num_inference_steps=1).images[0]
        self.cleanup_memory()
        logger.info("SDXL warmup complete.")

# Global instance
model_manager = SDXLModelManager()
