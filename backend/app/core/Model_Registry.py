"""Typed view over the active AI models, derived from ``settings``.

This module used to be a hard-coded duplicate of the model configuration (and
declared ``video_engine = ffmpeg_pipeline`` long after real GPU video existed,
plus an ElevenLabs TTS entry while the pipeline actually used gTTS). It is now a
thin, read-only facade: ``settings`` is the single source of truth, and this
just names the models for logging/UI.
"""
from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class ModelConfig:
    name: str
    type: str
    local: bool = True
    endpoint: str | None = None


def _script_llm() -> ModelConfig:
    if settings.LLM_PROVIDER == "auto":
        name = "gemini" if settings.GEMINI_API_KEY else settings.LOCAL_LLM_MODEL
    elif settings.LLM_PROVIDER == "gemini":
        name = settings.GEMINI_MODEL
    else:
        name = settings.LOCAL_LLM_MODEL

    local = not name.startswith("gemini")
    return ModelConfig(
        name=name,
        type="llm",
        local=local,
        endpoint=None if local else "https://generativelanguage.googleapis.com",
    )


def _image_generator() -> ModelConfig:
    if settings.COMFYUI_ENABLED:
        return ModelConfig(
            name=settings.COMFYUI_CHECKPOINT,
            type="image",
            local=True,
            endpoint=settings.COMFYUI_URL,
        )
    return ModelConfig(name="diffusers-sdxl", type="image", local=True)


def _video_engine() -> ModelConfig:
    backend = settings.VIDEO_BACKEND
    if backend == "svd":
        return ModelConfig(name=settings.SVD_MODEL_ID, type="video", local=True)
    if backend == "ffmpeg":
        return ModelConfig(name="ffmpeg_kenburns", type="video", local=True)
    return ModelConfig(name=backend, type="video", local=True)


def _tts() -> ModelConfig:
    if settings.TTS_PROVIDER == "elevenlabs" and settings.ELEVENLABS_API_KEY:
        return ModelConfig(
            name="eleven_multilingual_v2",
            type="tts",
            local=False,
            endpoint="https://api.elevenlabs.io",
        )
    return ModelConfig(name=f"gTTS:{settings.TTS_LANGUAGE}", type="tts", local=True)


class ModelRegistry:
    """Read-only, settings-backed registry of the active models."""

    @property
    def models(self) -> dict:
        return {
            "script_llm": _script_llm(),
            "image_generator": _image_generator(),
            "video_engine": _video_engine(),
            "tts": _tts(),
        }

    def get(self, key: str) -> ModelConfig:
        return self.models[key]


registry = ModelRegistry()
