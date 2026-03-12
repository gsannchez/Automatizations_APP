import os
from celery import Celery

# Configuración de Redis (asumiendo localhost por defecto)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Load all models for SQLAlchemy registry
from app.models.user import User
from app.models.channel import Channel
from app.models.template import Template
from app.models.generated_video import GeneratedVideo
from app.models.video_job import VideoJob
from app.models.asset import Asset


celery_app = Celery(
    "auto_video_maker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Configuración específica para Windows (solo si es necesario, pero pool=solo se pasa al worker)
    # worker_pool = 'solo' 
)

if __name__ == "__main__":
    celery_app.start()
