"""Narration synthesis.

``synthesize`` is the single entry point used by the pipeline; it routes to gTTS
or ElevenLabs according to ``settings.TTS_PROVIDER``.
"""
from .provider import synthesize
from .voice_registry import VoiceRegistry

__all__ = ["synthesize", "VoiceRegistry"]
