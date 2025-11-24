from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from ...core.database import engine
from ...models.template import Template
from ...schemas.ai_schema import AIScriptRequest, AIScriptResponse
from ...services.script_generator import ScriptGenerator

router = APIRouter()

@router.post("/generate-script", response_model=AIScriptResponse)
def generate_script(data: AIScriptRequest):
    """
    Genera un guion utilizando el servicio ScriptGenerator.
    """
    # 1. Obtener template
    with Session(engine) as session:
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
