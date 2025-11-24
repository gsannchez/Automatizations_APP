import requests
import base64
import os
from typing import Optional, Dict, Any

class Automatic1111Client:
    def __init__(self, base_url: str = "http://127.0.0.1:7861"):
        self.base_url = base_url
        self.default_negative_prompt = "bad quality, blurry, watermark, text, signature, distorted, deformed, lowres, error, cropped, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, out of frame, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck"
        
    def generate_image(
        self, 
        prompt: str, 
        negative_prompt: str = "", 
        width: int = 1024, 
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0,
        sampler_name: str = "DPM++ 2M Karras",
        seed: int = -1,
        restore_faces: bool = False,
        enable_hr: bool = False
    ) -> Optional[bytes]:
        """
        Genera una imagen usando la API de Automatic1111.
        """
        
        full_negative_prompt = f"{self.default_negative_prompt}, {negative_prompt}".strip(", ")

        payload = {
            "prompt": prompt,
            "negative_prompt": full_negative_prompt,
            "steps": steps,
            "sampler_name": sampler_name,
            "width": width,
            "height": height,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "restore_faces": restore_faces,
            "enable_hr": enable_hr,
            # Opciones avanzadas por defecto
            "hr_scale": 2 if enable_hr else 1,
            "hr_upscaler": "R-ESRGAN 4x+" if enable_hr else None,
        }

        try:
            response = requests.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload)
            response.raise_for_status()
            data = response.json()

            if "images" not in data or not data["images"]:
                print("[ERROR] A1111 response did not contain images.")
                return None

            # Automatic1111 devuelve las imágenes en base64
            b64_image = data["images"][0]
            return base64.b64decode(b64_image)

        except requests.exceptions.ConnectionError:
             print(f"[ERROR] Could not connect to A1111 at {self.base_url}. Is it running?")
             return None
        except Exception as e:
            print(f"[ERROR] A1111 image generation failed: {e}")
            return None

    def get_options(self) -> Dict[str, Any]:
        """Obtiene la configuración actual de A1111."""
        try:
            response = requests.get(f"{self.base_url}/sdapi/v1/options")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get options: {e}")
            return {}

# Instancia global para uso rápido si se prefiere no instanciar
# Pero se recomienda usar la clase.
# client = Automatic1111Client()
# generate_image_with_a1111 = client.generate_image
