"""
Self-contained end-to-end pipeline test.
Calls Ollama, ComfyUI, and ElevenLabs (or gTTS fallback) directly via HTTP.
Run from backend dir:  .\venv\Scripts\python scripts\test_simple_video.py
"""
import asyncio
import json
import os
import re
import time
import sys
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
OLLAMA_URL  = "http://192.168.1.41:11434"
OLLAMA_MODEL = "llama3.1:8b-instruct-q4_K_M"

COMFYUI_URL = "http://localhost:8188"
COMFYUI_CKPT = "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE   = "21m00Tcm4TlvDq8ikWAM"  # Rachel
ELEVENLABS_MODEL   = "eleven_multilingual_v2"

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. OLLAMA — script generation
# ---------------------------------------------------------------------------
async def generate_script(topic: str) -> list[dict]:
    """Ask Ollama to produce a JSON list of scenes."""
    prompt = f"""You are a professional short-video scriptwriter.
Create a script for a 60-second educational video about: "{topic}"

RULES:
1. Reply ONLY with valid JSON — no markdown, no explanation.
2. Return a JSON array of scene objects.

EXPECTED FORMAT:
[
  {{
    "text": "Exact voiceover text for the narrator.",
    "duration": 8,
    "image_prompt": "Detailed Stable Diffusion XL prompt in English, cinematic, 8k."
  }}
]

Generate between 4 and 6 scenes. Keep each scene under 15 seconds."""

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": "You are a JSON-only scriptwriter. Never output anything except valid JSON."},
            {"role": "user", "content": prompt},
        ],
    }
    print(f"  -> Calling Ollama at {OLLAMA_URL} ...")
    async with httpx.AsyncClient(timeout=600.0) as client:
        r = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        r.raise_for_status()
        raw = r.json()["message"]["content"]

    # Extract JSON array from response
    m = re.search(r"\[.*\]", raw, re.DOTALL)
    if not m:
        raise ValueError(f"Ollama did not return valid JSON array. Raw:\n{raw}")
    return json.loads(m.group(0))


# ---------------------------------------------------------------------------
# 2. COMFYUI — image generation
# ---------------------------------------------------------------------------
def _build_workflow(prompt: str, negative: str, seed: int, w: int = 768, h: int = 768) -> dict:
    return {
        "3": {"class_type": "KSampler", "inputs": {
            "cfg": 7, "denoise": 1, "latent_image": ["5", 0], "model": ["4", 0],
            "negative": ["7", 0], "positive": ["6", 0],
            "sampler_name": "euler", "scheduler": "normal", "seed": seed, "steps": 25}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": COMFYUI_CKPT}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"batch_size": 1, "height": h, "width": w}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": negative}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "pipeline_test", "images": ["8", 0]}},
    }


async def generate_image(prompt: str, out_path: Path, seed: int = 42) -> Path:
    negative = "bad quality, blurry, watermark, text, deformed"
    workflow = _build_workflow(prompt, negative, seed)

    async with httpx.AsyncClient(timeout=600.0) as client:
        # Free VRAM first
        try:
            await client.post(f"{COMFYUI_URL}/free", json={"unload_models": False, "free_memory": True})
        except Exception:
            pass

        # Queue
        r = await client.post(f"{COMFYUI_URL}/prompt", json={"prompt": workflow})
        if r.status_code != 200:
            raise RuntimeError(f"ComfyUI queue error {r.status_code}: {r.text}")
        prompt_id = r.json()["prompt_id"]
        print(f"     Queued prompt {prompt_id}, waiting...")

        # Poll
        while True:
            h = await client.get(f"{COMFYUI_URL}/history/{prompt_id}")
            data = h.json()
            if prompt_id in data:
                break
            await asyncio.sleep(2)

        # Check for errors
        entry = data[prompt_id]
        status_info = entry.get("status", {})
        if status_info.get("status_str") == "error":
            messages = status_info.get("messages", [])
            error_detail = "Unknown error"
            for msg in messages:
                if isinstance(msg, list) and msg[0] == "execution_error":
                    error_detail = msg[1].get("exception_message", error_detail)
                    break
            raise RuntimeError(f"ComfyUI execution failed: {error_detail}")

        # Extract image filename
        outputs = entry.get("outputs", {})
        image_output = None
        for node_id, node_out in outputs.items():
            if "images" in node_out and node_out["images"]:
                image_output = node_out["images"][0]
                break
        if not image_output:
            raise RuntimeError(f"ComfyUI produced no image output for prompt {prompt_id}")

        # Download
        filename = image_output["filename"]
        img = await client.get(f"{COMFYUI_URL}/view", params={"filename": filename})
        img.raise_for_status()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(img.content)
    return out_path


# ---------------------------------------------------------------------------
# 3. AUDIO — ElevenLabs with gTTS fallback
# ---------------------------------------------------------------------------
async def generate_audio(text: str, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Try ElevenLabs first
    if ELEVENLABS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE}",
                    headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
                    json={
                        "text": text,
                        "model_id": ELEVENLABS_MODEL,
                        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
                    },
                )
                r.raise_for_status()
                out_path.write_bytes(r.content)
                return out_path
        except Exception as e:
            print(f"     ElevenLabs failed ({e}), falling back to gTTS")

    # Fallback: gTTS (offline-ish, free)
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en")
        tts.save(str(out_path))
        return out_path
    except Exception as e:
        print(f"     gTTS also failed: {e}")
        return out_path


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
async def main():
    topic = "The process of photosynthesis explained simply"
    print(f"=== PIPELINE TEST: '{topic}' ===\n")

    # --- Step 1: Script ---
    print("[1/3] Generating script (Ollama)...")
    scenes = await generate_script(topic)
    print(f"  OK: {len(scenes)} scenes generated.\n")
    for i, s in enumerate(scenes):
        print(f"  Scene {i+1}: {s.get('text', '')[:60]}...")

    # --- Step 2: Audio ---
    print("\n[2/3] Generating audio...")
    audio_paths = []
    for i, s in enumerate(scenes):
        txt = s.get("text", "")
        if not txt:
            continue
        out = OUTPUT_DIR / f"audio_{i+1}.mp3"
        print(f"  Scene {i+1}...")
        p = await generate_audio(txt, out)
        audio_paths.append(p)
        print(f"  -> {p}")

    # --- Step 3: Images ---
    print("\n[3/3] Generating images (ComfyUI)...")
    image_paths = []
    for i, s in enumerate(scenes):
        prompt = s.get("image_prompt") or s.get("text", "landscape")
        out = OUTPUT_DIR / f"scene_{i+1}.png"
        print(f"  Scene {i+1}...")
        try:
            p = await generate_image(f"{prompt}, high quality, cinematic, masterpiece", out, seed=42 + i)
            image_paths.append(p)
            print(f"  -> {p}")
        except Exception as e:
            print(f"  ERROR: {e}")

    # --- Summary ---
    print("\n=== RESULTS ===")
    print(f"Audio files : {len(audio_paths)}")
    print(f"Image files : {len(image_paths)}")
    print(f"Output dir  : {OUTPUT_DIR.resolve()}")
    if audio_paths and image_paths:
        print("\nAll assets ready. FFmpeg composition can proceed.")
    else:
        print("\nSome assets missing — check errors above.")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
