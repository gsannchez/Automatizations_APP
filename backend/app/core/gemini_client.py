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
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config={
                # Velocidad y coherencia
                "temperature": 0.7,
                "top_p": 0.95,

                # Lo más importante:
                # Gemini ahora MANTIENE JSON puro
                "response_mime_type": "application/json"
            }
        )

        response = model.generate_content(prompt)

        # Limpieza básica (por seguridad)
        if not response or not response.text:
            raise RuntimeError("Gemini devolvió una respuesta vacía.")

        return response.text.strip()

    except Exception as e:
        raise RuntimeError(f"Error al generar contenido con Gemini: {e}")
