from sqlmodel import SQLModel, Field
from typing import Optional

class Channel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    tags: Optional[str] = None  # Ej: "motivacion,shorts,animales"
    export_path: Optional[str] = None
