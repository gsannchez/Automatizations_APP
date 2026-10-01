"""Minimal TTS package shim for legacy imports used by tasks and tests."""
from .elevenlabs_tts import ElevenLabsTTS
from .voice_registry import VoiceRegistry

__all__ = ["ElevenLabsTTS", "VoiceRegistry"]
