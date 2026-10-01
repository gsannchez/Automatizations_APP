import asyncio

class ElevenLabsTTS:
    """Lightweight shim for ElevenLabs TTS used in tasks/tests.

    This class provides an async `generate_audio` method returning a fake path
    when used in unit tests or simple dev runs. Replace with real SDK client
    integration when available.
    """
    async def generate_audio(self, text: str, voice_id: str, style: str = "neutral") -> str:
        # In production, integrate with the ElevenLabs SDK here.
        # For now, simulate quick generation by returning a deterministic path.
        await asyncio.sleep(0)
        return f"generated_audio/{voice_id}_{abs(hash(text)) % 100000}.mp3"
