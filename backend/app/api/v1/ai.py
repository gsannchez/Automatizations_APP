import json
import logging
import re

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from ...core.database import sync_engine
from ...core.llm_client import llm_client
from ...models.template import Template
from ...schemas.ai_schema import (
    AIScriptRequest,
    AIScriptResponse,
    AITextEnhanceRequest,
    AITextEnhanceResponse,
)
from ...services.script_generator import ScriptGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-script", response_model=AIScriptResponse)
def generate_script(data: AIScriptRequest):
    """
    Genera un guion utilizando el servicio ScriptGenerator.
    """
    # 1. Obtener template
    # Verify template exists
    # Note: data.template_id handles both int and UUID due to Union in schema,
    # but DB PK is UUID. SQLModel/SQLAlchemy should handle type coercion if needed,
    # but better to cast if we know it's UUID.

    with Session(sync_engine) as session:
        template = session.get(Template, data.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

    # 2. Usar el servicio generador
    generator = ScriptGenerator()
    try:
        response = generator.generate(data, template)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


_ENHANCE_PROMPT = """\
Eres un editor de contenido para redes sociales.
Mejora el siguiente título y tema para que sean más atractivos y claros,
sin cambiar su significado. Mantén el mismo idioma.

Título actual: {title}
Tema actual: {topic}

RESPONDE EXCLUSIVAMENTE CON UN OBJETO JSON, sin texto adicional ni bloques
de código:
{{"title": "<título mejorado>", "topic": "<tema mejorado>"}}
"""


@router.post("/enhance-text", response_model=AITextEnhanceResponse)
async def enhance_text(data: AITextEnhanceRequest):
    """Mejora título/topic con el LLM local (Ollama), devolviendo JSON.

    The Angular ``ai.service.ts::enhanceText`` consumes this endpoint.
    """
    prompt = _ENHANCE_PROMPT.format(title=data.title, topic=data.topic)

    try:
        raw = await llm_client.generate(prompt, json_mode=True, temperature=0.7)
    except Exception as exc:
        logger.error("enhance-text LLM call failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"LLM no disponible: {exc}")

    # The model sometimes wraps the JSON in prose even in json mode — pull out
    # the first object rather than failing the request.
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail="El modelo no devolvió JSON válido.")

    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"JSON inválido del modelo: {exc}")

    return AITextEnhanceResponse(
        title=parsed.get("title") or data.title,
        topic=parsed.get("topic") or data.topic,
    )
