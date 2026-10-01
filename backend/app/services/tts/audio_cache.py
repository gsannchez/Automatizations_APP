"""
app/services/tts/audio_cache.py

Caches audio generations to avoid duplicate ElevenLabs API calls.
"""
import os
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AudioCache:
    def __init__(self, cache_dir: str = "media/cache/audio"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_hash(self, text: str, voice_id: str, model: str, style: str) -> str:
        data = f"{text}_{voice_id}_{model}_{style}".encode("utf-8")
        return hashlib.md5(data).hexdigest()

    def get_cached_audio(self, text: str, voice_id: str, model: str, style: str) -> Optional[str]:
        audio_hash = self._generate_hash(text, voice_id, model, style)
        path = os.path.join(self.cache_dir, f"{audio_hash}.mp3")
        
        if os.path.exists(path) and os.path.getsize(path) > 512:
            logger.info(f"Audio cache HIT for hash: {audio_hash}")
            return os.path.abspath(path)
            
        return None

    def get_cache_path(self, text: str, voice_id: str, model: str, style: str) -> str:
        audio_hash = self._generate_hash(text, voice_id, model, style)
        return os.path.abspath(os.path.join(self.cache_dir, f"{audio_hash}.mp3"))
