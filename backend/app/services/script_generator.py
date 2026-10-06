import asyncio
import json
import logging
import re
from typing import List, Optional

from fastapi import HTTPException

from ..core.config import settings
from ..core.gemini_client import generate_gemini_prompt
from ..core.llm_client import llm_client
from ..schemas.ai_schema import AIScriptRequest, AIScriptResponse, AIScene
from ..models.template import Template

logger = logging.getLogger(__name__)


class ScriptGenerator:
    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------
    def _build_system_prompt(self, data: AIScriptRequest, template: Optional[Template]) -> str:
        """Construye el prompt avanzado para el LLM."""

        # A missing template must not abort scripting — fall back to free-form.
        structure = template.structure_json if template is not None else "[]"

        platform_instructions = ""
        if data.platform.lower() == "tiktok":
            platform_instructions = "Estilo dinámico, rápido, con gancho en los primeros 3 segundos. Uso de jerga actual si aplica."
        elif data.platform.lower() == "youtube":
            platform_instructions = "Estilo didáctico pero entretenido. Estructura clara: Intro, Desarrollo, Conclusión."
        elif data.platform.lower() == "instagram":
            platform_instructions = "Estilo visual y estético. Frases cortas e inspiradoras."
        else:
            platform_instructions = "Estilo general para redes sociales."

        tone_instruction = f"Tono: {data.tone}" if data.tone else "Tono: Neutro y profesional"
        audience_instruction = f"Audiencia objetivo: {data.target_audience}" if data.target_audience else "Audiencia: General"
        language_instruction = f"Idioma de salida: {data.language}" if data.language else "Idioma: Español"

        prompt = f"""
        Actúa como un guionista y director de arte experto para redes sociales.
        Genera un guion para un video corto sobre: "{data.topic}"

        CONTEXTO:
        - Plataforma: {data.platform} ({platform_instructions})
        - {tone_instruction}
        - {audience_instruction}
        - {language_instruction}

        ESTRUCTURA REQUERIDA (Basada en Template):
        {structure}

        REGLAS DE FORMATO:
        1. RESPONDE EXCLUSIVAMENTE CON JSON VÁLIDO (un array).
        2. NO incluyas texto introductorio ni conclusiones fuera del JSON.
        3. NO uses bloques de código markdown (```json ... ```). Solo el JSON crudo.
        4. Cada objeto del array es una escena.

        FORMATO JSON ESPERADO:
        [
          {{
            "text": "Texto exacto que dirá el narrador (voiceover).",
            "duration": <duración en segundos, número entero>,
            "image_prompt": "Prompt detallado para generar la imagen de fondo con IA. EN INGLÉS, muy descriptivo.",
            "visual_style": "Estilo visual global, p.ej. 'cinematic photorealistic, volumetric light, 35mm'",
            "camera_move": "Movimiento de cámara: 'slow push in', 'pan left', 'static', 'tilt up'...",
            "character": "Identificador del personaje si aparece (p.ej. 'host_male_30s'); reutilízalo si se repite",
            "emotion": "Emoción dominante: 'curious', 'excited', 'serious'...",
            "negative_prompt": "Lo que NO debe aparecer (p.ej. 'blurry, text, watermark, deformed hands')",
            "seed": <entero estable para mantener consistencia entre escenas>,
            "on_screen_text": "Texto breve para superponer/caption (puede ir vacío)",
            "sfx": "Efecto de sonido opcional (puede ir vacío)"
          }}
        ]

        CONSEJOS:
        - Usa palabras clave de iluminación, estilo y composición en image_prompt.
        - Mantén el MISMO personaje, estilo y seed coherentes a lo largo de las escenas.
        - Ejemplo de image_prompt: "Cinematic shot of a futuristic city, neon lights, cyberpunk style, 8k, highly detailed"
        """
        return prompt

    # ------------------------------------------------------------------
    # Provider selection (Gemini real, fallback a Ollama local)
    # ------------------------------------------------------------------
    def _call_llm(self, data: AIScriptRequest, prompt: str) -> str:
        provider = (settings.LLM_PROVIDER or "auto").lower()
        api_key = data.api_key or settings.GEMINI_API_KEY
        model_name = data.model_name or settings.GEMINI_MODEL

        if provider in ("auto", "gemini"):
            try:
                # ``generate_gemini_prompt`` is called through the module-level name
                # so tests can patch ``app.services.script_generator.generate_gemini_prompt``.
                return generate_gemini_prompt(
                    prompt, api_key=api_key, model_name=model_name
                )
            except Exception as exc:
                if provider == "gemini":
                    raise
                logger.warning("Gemini no disponible (%s); usando LLM local", exc)

        # Fallback: local Ollama (qwen2.5) — llm_client is async, run it synchronously.
        return asyncio.run(llm_client.generate(prompt, json_mode=True))

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_scenes(raw_response: str) -> List[dict]:
        json_match = re.search(r"\[.*\]", raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))

        # Fallback: a single object instead of a list.
        single = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if single:
            return [json.loads(single.group(0))]

        raise ValueError("El modelo no devolvió un JSON válido.")

    def generate(self, data: AIScriptRequest, template: Optional[Template]) -> AIScriptResponse:
        """Genera el guion orquestando la llamada al LLM y el parseo."""
        prompt = self._build_system_prompt(data, template)

        try:
            raw_response = self._call_llm(data, prompt)

            try:
                scenes_data = self._extract_scenes(raw_response)
            except (ValueError, json.JSONDecodeError):
                # One repair attempt before giving up.
                logger.warning("JSON inválido del LLM; reintentando reparación")
                repair_prompt = (
                    f"{prompt}\n\nTU RESPUESTA ANTERIOR NO ERA JSON VÁLIDO. "
                    "Devuelve ÚNICAMENTE el array JSON, sin texto adicional."
                )
                raw_response = self._call_llm(data, repair_prompt)
                scenes_data = self._extract_scenes(raw_response)

            scenes = [AIScene(**scene) for scene in scenes_data]
            return AIScriptResponse(scenes=scenes)

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error al decodificar el JSON generado por la IA.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en generación de guion: {str(e)}")
