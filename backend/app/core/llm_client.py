import httpx
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from .config import settings

logger = logging.getLogger(__name__)

class LocalLLMClient:
    def __init__(self):
        self.base_url = settings.LOCAL_LLM_URL.rstrip('/')
        self.model = settings.LOCAL_LLM_MODEL

    async def _post_request(self, endpoint: str, payload: dict, retries: int = 3, backoff: float = 2.0) -> dict:
        url = f"{self.base_url}{endpoint}"
        
        # Instantiate the client per-request to avoid event loop attachment issues
        async with httpx.AsyncClient(timeout=600.0) as client:
            for attempt in range(1, retries + 1):
                try:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    return response.json()
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    logger.warning(f"LLM request failed (attempt {attempt}/{retries}): {e}")
                    if attempt == retries:
                        raise RuntimeError(f"Local LLM API error after {retries} attempts: {e}")
                    await asyncio.sleep(backoff * attempt)
        return {}

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False, temperature: float = 0.7) -> str:
        """
        Calls the /api/generate endpoint of Ollama.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if system_prompt:
            payload["system"] = system_prompt
        if json_mode:
            payload["format"] = "json"

        response_data = await self._post_request("/api/generate", payload)
        
        response_text = response_data.get("response", "")
        if not response_text:
            raise ValueError("Local LLM returned an empty response.")
        
        return response_text.strip()

    async def chat(self, messages: List[Dict[str, str]], json_mode: bool = False, temperature: float = 0.7) -> str:
        """
        Calls the /api/chat endpoint of Ollama.
        `messages` should be a list of dicts like: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if json_mode:
            payload["format"] = "json"

        response_data = await self._post_request("/api/chat", payload)
        
        response_text = response_data.get("message", {}).get("content", "")
        if not response_text:
            raise ValueError("Local LLM chat returned an empty response.")
        
        return response_text.strip()

llm_client = LocalLLMClient()
