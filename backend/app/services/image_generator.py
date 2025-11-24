import os
import hashlib
from .automatic1111_client import Automatic1111Client

OUTPUT_DIR = "generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ImageGenerator:
    def __init__(self):
        self.client = Automatic1111Client()

    def _get_cache_filename(self, prompt: str) -> str:
        """Genera un nombre de archivo único basado en el hash del prompt."""
        hash_object = hashlib.md5(prompt.encode())
        return os.path.join(OUTPUT_DIR, f"{hash_object.hexdigest()}.png")

    def generate_images_for_scenes(self, scenes):
        """
        Genera una imagen por escena usando AUTOMATIC1111.
        Devuelve la lista de rutas a las imágenes generadas.
        """
        image_paths = []

        for idx, scene in enumerate(scenes):
            # Obtener prompt
            base_prompt = scene.get("image_prompt") or scene.get("text")
            
            # Mejorar prompt automáticamente (simple)
            enhanced_prompt = f"{base_prompt}, high quality, detailed, 8k"

            # Verificar caché
            cache_path = self._get_cache_filename(enhanced_prompt)
            if os.path.exists(cache_path):
                print(f"🟢 Using cached image for scene {idx}")
                image_paths.append(cache_path)
                continue

            print(f"🎨 Generating image for scene {idx}...")
            img_bytes = self.client.generate_image(
                prompt=enhanced_prompt,
                steps=30,
                cfg_scale=7.0
            )

            if img_bytes is None:
                # fallback: imagen negra
                print(f"🔴 Failed to generate image for scene {idx}, using fallback.")
                filename = os.path.join(OUTPUT_DIR, f"fallback_{idx}.png")
                with open(filename, "wb") as f:
                    f.write(self._generate_black_image())
                image_paths.append(filename)
                continue

            # Guardar imagen (y en caché implícitamente por el nombre)
            with open(cache_path, "wb") as f:
                f.write(img_bytes)

            image_paths.append(cache_path)

        return image_paths

    def _generate_black_image(self) -> bytes:
        from PIL import Image
        import io

        img = Image.new("RGB", (1024, 1024), color=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

# Función wrapper para compatibilidad hacia atrás si es necesario
def generate_images_for_scenes(scenes):
    generator = ImageGenerator()
    return generator.generate_images_for_scenes(scenes)
