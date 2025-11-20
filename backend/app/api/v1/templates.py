from fastapi import APIRouter, HTTPException
from sqlmodel import select, Session
from ...core.database import engine
from ...models.template import Template
from ...schemas.template_schema import TemplateCreate, TemplateRead

router = APIRouter(tags=["Templates"])

@router.get("/", response_model=list[TemplateRead])
def list_templates():
    with Session(engine) as session:
        return session.exec(select(Template)).all()

@router.post("/", response_model=TemplateRead)
def create_template(data: TemplateCreate):
    with Session(engine) as session:
        template = Template(**data.dict())
        session.add(template)
        session.commit()
        session.refresh(template)
        return template

@router.get("/{template_id}", response_model=TemplateRead)
def get_template(template_id: int):
    with Session(engine) as session:
        template = session.get(Template, template_id)
        if not template:
            raise HTTPException(404, "Template not found")
        return template

@router.delete("/{template_id}")
def delete_template(template_id: int):
    with Session(engine) as session:
        template = session.get(Template, template_id)
        if not template:
            raise HTTPException(404, "Template not found")
        session.delete(template)
        session.commit()
        return {"deleted": True}
