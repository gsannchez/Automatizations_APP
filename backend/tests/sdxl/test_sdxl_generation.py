"""
tests/sdxl/test_sdxl_generation.py

Phase SDXL
Validates real image generation integration without running full model if in test mode.
For real generation validation, it mocks the slow pipeline call but tests the structural flow.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from app.services.ai.image_generation.sdxl_generator import SDXLGenerator
from app.services.ai.image_generation.prompt_enhancer import PromptEnhancer
from app.services.ai.image_generation.image_cache import ImageCache

@pytest.mark.asyncio
@patch('app.services.ai.image_generation.sdxl_generator.SDXLGenerator._run_inference_sync')
@patch('app.services.ai.image_generation.gpu_image_guard.GPUImageGuard.wait_for_vram')
async def test_generation_flow(mock_vram, mock_inference, tmp_path):
    mock_vram.return_value = True
    
    # Setup mock file to pass validation
    test_img = tmp_path / "test_out.png"
    
    def mock_run(*args, **kwargs):
        from PIL import Image
        img = Image.new('RGB', (1024, 1024), color = 'red')
        img.save(test_img)
        
    mock_inference.side_effect = mock_run

    generator = SDXLGenerator()
    # override cache dir for test
    generator.cache.cache_dir = str(tmp_path)
    
    path = await generator.generate_image(
        prompt="A cute cat",
        negative_prompt="",
        width=1024,
        height=1024,
        style="CINEMATIC",
        output_path=str(test_img)
    )
    
    assert os.path.exists(path)
    assert path == str(test_img)

def test_prompt_enhancer():
    enhancer = PromptEnhancer()
    res = enhancer.enhance("Test", "BODYCAM")
    assert "bodycam" in res.lower()
    
def test_image_cache():
    cache = ImageCache()
    h = cache._generate_hash("A", "B", 1)
    assert h is not None
