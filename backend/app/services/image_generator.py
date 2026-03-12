import hashlib
import io
from .automatic1111_client import Automatic1111Client
from .storage import storage

OUTPUT_DIR = "generated_images"

class ImageGenerator:
    def __init__(self):
        self.client = Automatic1111Client()

    def _get_cache_filename(self, prompt: str) -> str:
        """Genera un nombre de archivo único basado en el hash del prompt."""
        hash_object = hashlib.md5(prompt.encode())
        # Ruta relativa
        return f"{OUTPUT_DIR}/{hash_object.hexdigest()}.png"

    def generate_images_for_scenes(self, scenes):
        """
        Genera una imagen por escena usando AUTOMATIC1111.
        Devuelve la lista de rutas relativas a las imágenes generadas.
        """
        image_paths = []

        for idx, scene in enumerate(scenes):
            # Obtener prompt
            base_prompt = scene.get("image_prompt") or scene.get("text")
            
            # Mejorar prompt automáticamente (simple)
            enhanced_prompt = f"{base_prompt}, high quality, detailed, 8k"
            
            # Cache path relativo
            cache_path = self._get_cache_filename(enhanced_prompt)
            
            # TODO: Verificar caché en storage
            # if storage.exists(cache_path): ...

            print(f"🎨 Generating image for scene {idx}...")
            img_bytes = self.client.generate_image(
                prompt=enhanced_prompt,
                steps=30,
                cfg_scale=7.0
            )

            if img_bytes is None:
                # fallback: imagen negra
                print(f"🔴 Failed to generate image for scene {idx}, using fallback.")
                fallback_path = f"{OUTPUT_DIR}/fallback_{idx}.png"
                black_img = self._generate_black_image()
                storage.save(black_img, fallback_path)
                image_paths.append(fallback_path)
                continue

            # Guardar imagen en storage
            storage.save(img_bytes, cache_path)
            image_paths.append(cache_path)

        return image_paths

    def _generate_black_image(self) -> bytes:
        from PIL import Image
        
        img = Image.new("RGB", (1024, 1024), color=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

# Función wrapper para compatibilidad hacia atrás si es necesario
def generate_images_for_scenes(scenes):
    generator = ImageGenerator()
    return generator.generate_images_for_scenes(scenes)
