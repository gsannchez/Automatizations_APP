"""Narration synthesis, routed by ``settings.TTS_PROVIDER``.

``gtts`` (free, needs network) is the default so the pipeline works out of the
box. ``elevenlabs`` is used when a key is configured; any failure there degrades
to gTTS rather than failing the video.
"""
from __future__ import annotations

import io
import logging
from typing import Optional

from app.core.config import settings
from app.services.storage import storage

logger = logging.getLogger(__name__)


def synthesize(text: str, storage_key: str, language: Optional[str] = None) -> str:
    """Render *text* to an mp3 stored at *storage_key*; returns the storage key."""
    clean = (text or "").replace("*", "").strip()
    if not clean:
        raise ValueError("TTS text is empty")

    lang = language or settings.TTS_LANGUAGE

    if settings.TTS_PROVIDER == "elevenlabs" and settings.ELEVENLABS_API_KEY:
        try:
            return _elevenlabs(clean, storage_key)
        except Exception as exc:
            logger.warning("ElevenLabs TTS failed (%s); falling back to gTTS", exc)

    return _gtts(clean, storage_key, lang)


def _gtts(text: str, storage_key: str, lang: str) -> str:
    from gtts import gTTS

    buf = io.BytesIO()
    gTTS(text=text, lang=lang, slow=False).write_to_fp(buf)
    buf.seek(0)
    storage.save(buf, storage_key)
    logger.info("TTS (gTTS/%s) written to %s", lang, storage_key)
    return storage_key


def _elevenlabs(text: str, storage_key: str) -> str:
    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=_resolve_voice(),
        model_id="eleven_multilingual_v2",
    )
    buf = io.BytesIO(b"".join(audio))
    buf.seek(0)
    storage.save(buf, storage_key)
    logger.info("TTS (ElevenLabs) written to %s", storage_key)
    return storage_key


def _resolve_voice() -> str:
    from app.services.tts.voice_registry import VoiceRegistry

    return VoiceRegistry().get_voice("narrator")["voice_id"]
