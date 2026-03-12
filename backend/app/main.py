"""FastAPI application entry point — Phase 3 SaaS platform."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .core.database import init_db
from .core.limiter import limiter
from .api.v1.channels import router as channels_router
from .api.v1.templates import router as templates_router
from .api.v1.videos import router as videos_router
from .api.v1.ai import router as ai_router
from .api.v1.auth import router as auth_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Auto Video Maker API",
    description="Multi-user SaaS platform for automated video generation.",
    version="3.0.0",
)

# ---------------------------------------------------------------------------
# Rate limiting (slowapi)
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# CORS — allow Angular dev server
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    await init_db()
    from .core.scheduler import start_scheduler
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    from .core.scheduler import stop_scheduler
    stop_scheduler()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "backend ok", "version": "3.0.0"}


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router,      prefix="/api/v1/auth")
app.include_router(channels_router,  prefix="/api/v1/channels")
app.include_router(templates_router, prefix="/api/v1/templates")
app.include_router(videos_router,    prefix="/api/v1/videos")
app.include_router(ai_router,        prefix="/api/v1/ai")
