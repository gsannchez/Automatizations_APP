import os
from gtts import gTTS
from typing import Optional

class TTSService:
    def __init__(self, output_dir: str = "generated_audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_audio(self, text: str, filename: str, lang: str = "es") -> str:
        """
        Genera un archivo de audio MP3 a partir de texto usando gTTS.
        Devuelve la ruta absoluta del archivo generado.
        """
        try:
            # Limpiar texto básico
            clean_text = text.replace("*", "").strip()
            
            if not clean_text:
                raise ValueError("El texto para TTS está vacío.")

            path = os.path.join(self.output_dir, filename)
            
            # Si ya existe, no regenerar (caché simple)
            if os.path.exists(path):
                return os.path.abspath(path)

            tts = gTTS(text=clean_text, lang=lang, slow=False)
            tts.save(path)
            
            return os.path.abspath(path)

        except Exception as e:
            print(f"[ERROR] TTS generation failed: {e}")
            raise e

# Instancia global
tts_service = TTSService()
