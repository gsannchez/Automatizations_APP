"""
app/services/ai/image_generation/image_quality.py

Phase SDXL
Validates generated images to detect black frames, corruption, and NaN pixels.
"""
import os
import logging
from PIL import Image, ImageStat

logger = logging.getLogger(__name__)

class ImageQualityValidator:
    def validate_image(self, path: str) -> bool:
        """Returns True if the image is valid, False otherwise."""
        if not os.path.exists(path):
            logger.error(f"Image validation failed: file not found at {path}")
            return False
            
        try:
            with Image.open(path) as img:
                img.verify() # Verify file integrity
            
            with Image.open(path) as img:
                # Check for completely black image (often happens with NaN/NSFW filter false positives)
                stat = ImageStat.Stat(img)
                if sum(stat.sum) == 0:
                    logger.error("Image validation failed: image is completely black.")
                    return False
                    
                # Check minimum resolution
                if img.width < 256 or img.height < 256:
                    logger.error(f"Image validation failed: resolution too small ({img.width}x{img.height})")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed due to corruption: {str(e)}")
            return False
