from sqlmodel import SQLModel, create_engine
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # muestra las consultas SQL
)

def init_db():
    SQLModel.metadata.create_all(engine)
