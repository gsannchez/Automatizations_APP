from fastapi import APIRouter, HTTPException
from sqlmodel import Session
from ...core.database import engine
from ...models.template import Template
from ...schemas.ai_schema import AIScriptRequest, AIScriptResponse, AIScene
from ...core.gemini_client import generate_gemini_prompt
import json
import re

router = APIRouter()

@router.post("/generate-script", response_model=AIScriptResponse)
def generate_script(data: AIScriptRequest):

    # 1. Obtener template
    with Session(engine) as session:
        template = session.get(Template, data.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

    # 2. Prompt optimizado
    prompt = f"""
Genera un guion para un video corto basado en este tema:

Tema: "{data.topic}"

Usa el siguiente template como referencia del número de escenas y duración:

Template:
{template.structure_json}

RESPONDE EXCLUSIVAMENTE CON JSON VÁLIDO.
SIN TEXTO FUERA DEL JSON.
SIN MARKDOWN.
SIN COMENTARIOS.

Debe ser EXACTAMENTE una lista JSON así:

[
  {{
    "text": "texto narrado",
    "duration": 3,
    "image_prompt": "prompt para generar imagen"
  }}
]
"""

    # 3. Llamar a Gemini
    try:
        raw = generate_gemini_prompt(prompt)
        print("🔵 RAW GEMINI RESPONSE:")
        print(raw)

        # Extraer JSON limpio
        json_match = re.search(r'\[.*\]', raw, re.DOTALL)
        if not json_match:
            raise HTTPException(
                status_code=500,
                detail=f"Gemini no devolvió JSON válido.\nRespuesta completa:\n{raw}"
            )

        clean_json = json_match.group(0)
        scenes_list = json.loads(clean_json)

        scenes = [AIScene(**scene) for scene in scenes_list]
        return AIScriptResponse(scenes=scenes)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation error: {e}")
