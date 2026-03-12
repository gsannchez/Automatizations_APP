import os
import google.generativeai as genai
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if not API_KEY:
    raise ValueError("❌ No se encontró la variable GEMINI_API_KEY en .env")

# Configurar cliente de Gemini
genai.configure(api_key=API_KEY)

def generate_gemini_prompt(prompt: str) -> str:
    """
    Envía un prompt a Gemini y devuelve SIEMPRE una respuesta en texto plano
    con MIME JSON garantizado.
    """

    try:
        # MOCK RESPONSE PARA EVITAR RATE LIMIT DE GEMINI DURANTE PRUEBAS
        import time
        time.sleep(2) # Simular latencia de red
        
        mock_response = """
        {
          "title": "La Revolución de la IA",
          "description": "Una mirada rápida al futuro de la inteligencia artificial.",
          "scenes": [
            {
              "type": "intro",
              "text": "Bienvenidos al futuro. La IA está cambiando todo.",
              "duration": 5,
              "image_prompt": "Futuristic glowing brain network digital art style"
            },
            {
              "type": "main",
              "text": "Desde automatización de tareas hasta asistencia médica, sus usos son infinitos.",
              "duration": 5,
              "image_prompt": "Robot doctor shaking hands with a human patient"
            }
          ]
        }
        """
        
        return mock_response.strip()

    except Exception as e:
        raise RuntimeError(f"Error al generar contenido con Gemini: {e}")
