from sqlmodel import SQLModel, Field
from typing import Optional

class Template(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None

    # JSON con estructura de escenas (texto, duración, animaciones)
    structure_json: Optional[str] = None  

    # Duración recomendada del vídeo (segundos)
    recommended_duration: Optional[int] = None

    # Música por defecto, estilo visual, etc.
    style: Optional[str] = None
