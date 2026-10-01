"""
app/services/ai/base/base_image_generator.py

Phase SDXL
Base interface for image generation to maintain decoupling and compatibility.
"""
from abc import ABC, abstractmethod
from typing import Optional

class BaseImageGenerator(ABC):
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        style: str,
        seed: Optional[int],
        output_path: str
    ) -> str:
        """
        Generates an image and returns the absolute path to the generated file.
        """
        pass
