from fastapi import FastAPI
from .core.database import init_db
from .api.v1.channels import router as channels_router
from .api.v1.templates import router as templates_router
from .api.v1.videos import router as videos_router
from .api.v1.ai import router as ai_router
import logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(title="Auto Video Maker Backend")

@app.on_event("startup")
async def on_startup():
    await init_db()
    from .core.scheduler import start_scheduler
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    from .core.scheduler import stop_scheduler
    stop_scheduler()

@app.get("/")
def root():
    return {"status": "backend ok"}

# Registrar routers
app.include_router(channels_router, prefix="/api/v1/channels")
app.include_router(templates_router, prefix="/api/v1/templates")
app.include_router(videos_router, prefix="/api/v1/videos")
app.include_router(ai_router, prefix="/api/v1/ai")



