"""
app/services/ai/image_generation/prompt_enhancer.py

Phase SDXL
Enhances base prompts into cinematic SDXL optimized prompts.
"""
import logging

logger = logging.getLogger(__name__)

class PromptEnhancer:
    STYLE_PRESETS = {
        "CINEMATIC": "Ultra realistic cinematic, dramatic lighting, highly detailed, cinematic composition, realistic textures, 35mm film look, depth of field, 8k resolution, masterpiece",
        "BODYCAM": "police bodycam footage, ultra realistic, motion blur, fisheye distortion, raw, unfiltered, grainy, found footage, realistic lighting",
        "CCTV": "security camera footage, cctv, low angle, black and white, highly detailed, noisy, realistic security camera",
        "HORROR": "dark horror, terrifying, macabre, deep shadows, cinematic lighting, ultra detailed, eerie mist, silent hill style, masterpiece",
        "TIKTOK_NATIVE": "vertical tiktok style, bright colorful, highly aesthetic, modern, influencer aesthetic, high quality smartphone camera, vivid colors",
        "MEME_REALISM": "hyper realistic meme, absurd, high quality render, detailed background, dramatic lighting on funny subject, vivid",
        "ANIME_EDIT": "high quality anime style, makoto shinkai, studio ghibli, beautiful lighting, detailed scenery, vivid colors, masterpiece"
    }

    NEGATIVE_PROMPT = (
        "blurry, low quality, deformed, watermark, extra fingers, "
        "bad anatomy, distorted face, text, logo, pixelated, ugly, missing limbs, "
        "poorly drawn face, mutation, mutated, lowres"
    )

    def enhance(self, base_prompt: str, style: str) -> str:
        """Appends style-specific modifiers to the base prompt."""
        style_modifier = self.STYLE_PRESETS.get(style.upper(), self.STYLE_PRESETS["CINEMATIC"])
        enhanced = f"{base_prompt}, {style_modifier}"
        logger.debug(f"Enhanced prompt: {enhanced}")
        return enhanced

    def get_negative_prompt(self, user_negative: str = "") -> str:
        """Combines system negative prompts with user provided ones."""
        if user_negative:
            return f"{self.NEGATIVE_PROMPT}, {user_negative}"
        return self.NEGATIVE_PROMPT
