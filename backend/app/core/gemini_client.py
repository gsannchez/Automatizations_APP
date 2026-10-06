"""Real Google Gemini client for script generation.

Replaces the previous hardcoded mock. Validation is deferred to call time so that
importing this module never fails when no API key is configured.
"""
import logging
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class GeminiUnavailable(RuntimeError):
    """Raised when Gemini cannot be used (no key, empty response, API error)."""


def _resolve_api_key(api_key: str | None) -> str | None:
    return api_key or os.getenv("GEMINI_API_KEY") or None


def generate_gemini_prompt(
    prompt: str,
    *,
    api_key: str | None = None,
    model_name: str | None = None,
    temperature: float = 0.9,
) -> str:
    """Send *prompt* to Gemini and return the raw text response.

    Args:
        prompt: The full instruction prompt.
        api_key: Per-user key override; falls back to ``GEMINI_API_KEY`` env var.
        model_name: Model override; falls back to ``GEMINI_MODEL`` env var.
        temperature: Sampling temperature.

    Raises:
        GeminiUnavailable: If no key is configured, or the model returns nothing.
    """
    resolved_key = _resolve_api_key(api_key)
    if not resolved_key:
        raise GeminiUnavailable("No GEMINI_API_KEY configured")

    model = model_name or DEFAULT_MODEL
    genai.configure(api_key=resolved_key)
    generative_model = genai.GenerativeModel(model)

    try:
        response = generative_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:
        # Older SDK/model combos reject response_mime_type — retry as plain text.
        logger.warning("Gemini JSON-mode call failed (%s); retrying as plain text", exc)
        response = generative_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature),
        )

    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise GeminiUnavailable("Gemini returned an empty response")
    return text
