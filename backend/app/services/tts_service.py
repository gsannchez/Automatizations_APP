import io
from gtts import gTTS
from typing import Optional
from .storage import storage

class TTSService:
    def __init__(self, output_dir: str = "generated_audio"):
        # output_dir ya no se usa como ruta absoluta, sino como prefijo en storage
        self.output_prefix = output_dir

    def generate_audio(self, text: str, filename: str, lang: str = "es") -> str:
        """
        Genera un archivo de audio MP3 a partir de texto usando gTTS.
        Devuelve la ruta relativa en el storage.
        """
        try:
            # Limpiar texto básico
            clean_text = text.replace("*", "").strip()
            
            if not clean_text:
                raise ValueError("El texto para TTS está vacío.")

            # Ruta relativa en storage
            storage_path = f"{self.output_prefix}/{filename}"
            
            # TODO: Implementar caché eficiente. Por ahora regeneramos o verificamos local si es local
            # if storage.exists(storage_path): return storage_path 

            tts = gTTS(text=clean_text, lang=lang, slow=False)
            
            # Guardar en buffer
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            
            # Guardar en storage
            storage.save(buf, storage_path)
            
            return storage_path

        except Exception as e:
            print(f"[ERROR] TTS generation failed: {e}")
            raise e

# Instancia global
tts_service = TTSService()
