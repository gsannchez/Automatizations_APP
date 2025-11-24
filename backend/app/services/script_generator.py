import json
import re
from typing import List, Optional
from fastapi import HTTPException
from ..core.gemini_client import generate_gemini_prompt
from ..schemas.ai_schema import AIScriptRequest, AIScriptResponse, AIScene
from ..models.template import Template

class ScriptGenerator:
    def __init__(self):
        pass

    def _build_system_prompt(self, data: AIScriptRequest, template: Template) -> str:
        """
        Construye el prompt avanzado para el LLM.
        """
        
        # Definir estilo según plataforma
        platform_instructions = ""
        if data.platform.lower() == "tiktok":
            platform_instructions = "Estilo dinámico, rápido, con gancho en los primeros 3 segundos. Uso de jerga actual si aplica."
        elif data.platform.lower() == "youtube":
            platform_instructions = "Estilo didáctico pero entretenido. Estructura clara: Intro, Desarrollo, Conclusión."
        elif data.platform.lower() == "instagram":
            platform_instructions = "Estilo visual y estético. Frases cortas e inspiradoras."
        else:
            platform_instructions = "Estilo general para redes sociales."

        # Definir tono
        tone_instruction = f"Tono: {data.tone}" if data.tone else "Tono: Neutro y profesional"

        # Definir audiencia
        audience_instruction = f"Audiencia objetivo: {data.target_audience}" if data.target_audience else "Audiencia: General"

        # Definir idioma
        language_instruction = f"Idioma de salida: {data.language}" if data.language else "Idioma: Español"

        prompt = f"""
        Actúa como un guionista experto para redes sociales.
        Genera un guion para un video corto sobre: "{data.topic}"

        CONTEXTO:
        - Plataforma: {data.platform} ({platform_instructions})
        - {tone_instruction}
        - {audience_instruction}
        - {language_instruction}

        ESTRUCTURA REQUERIDA (Basada en Template):
        {template.structure_json}

        REGLAS DE FORMATO:
        1. RESPONDE EXCLUSIVAMENTE CON JSON VÁLIDO.
        2. NO incluyas texto introductorio ni conclusiones fuera del JSON.
        3. NO uses bloques de código markdown (```json ... ```). Solo el JSON crudo.
        4. El formato debe ser una lista de objetos, donde cada objeto es una escena.
        
        FORMATO JSON ESPERADO:
        [
          {{
            "text": "Texto exacto que dirá el narrador (voiceover).",
            "duration": <duración en segundos, número entero>,
            "image_prompt": "Prompt detallado para generar la imagen de fondo con IA (Stable Diffusion). Debe ser en INGLÉS, muy descriptivo, estilo fotorealista o ilustración según el tono."
          }}
        ]

        CONSEJOS PARA EL PROMPT DE IMAGEN:
        - Usa palabras clave de iluminación, estilo y composición.
        - Ejemplo: "Cinematic shot of a futuristic city, neon lights, cyberpunk style, 8k resolution, highly detailed"
        """
        return prompt

    def generate(self, data: AIScriptRequest, template: Template) -> AIScriptResponse:
        """
        Genera el guion orquestando la llamada a Gemini y el parseo.
        """
        prompt = self._build_system_prompt(data, template)
        
        try:
            raw_response = generate_gemini_prompt(prompt)
            
            # Limpieza y extracción de JSON
            # A veces los LLM ponen ```json ... ``` aunque se les diga que no.
            json_match = re.search(r'\[.*\]', raw_response, re.DOTALL)
            
            if not json_match:
                # Intento de fallback si devuelve un objeto único en vez de lista
                json_match_single = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match_single:
                     # Si es un solo objeto, lo envolvemos en lista (aunque el prompt pide lista)
                     clean_json = f"[{json_match_single.group(0)}]"
                else:
                    print(f"🔴 ERROR GEMINI RESPONSE: {raw_response}")
                    raise ValueError("El modelo no devolvió un JSON válido.")
            else:
                clean_json = json_match.group(0)

            scenes_data = json.loads(clean_json)
            
            # Validar estructura
            scenes = [AIScene(**scene) for scene in scenes_data]
            
            return AIScriptResponse(scenes=scenes)

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error al decodificar el JSON generado por la IA.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error en generación de guion: {str(e)}")
