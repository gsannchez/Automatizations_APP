from dataclasses import dataclass

@dataclass
class ModelConfig:
    name: str
    type: str
    endpoint: str | None = None
    local: bool = True


class ModelRegistry:
    """
    Single source of truth for all AI models in the system.
    """

    def __init__(self):
        self.models = {
            # 🧠 TEXT / LLM
            "script_llm": ModelConfig(
                name="qwen2.5-instruct",
                type="llm",
                local=True
            ),

            "hook_llm": ModelConfig(
                name="qwen2.5-coder",
                type="llm",
                local=True
            ),

            # 🎨 IMAGES
            "image_generator": ModelConfig(
                name="stable-diffusion-xl",
                type="image",
                local=True
            ),

            # 🔊 AUDIO
            "tts": ModelConfig(
                name="elevenlabs",
                type="tts",
                local=False,
                endpoint="https://api.elevenlabs.io"
            ),

            # 🎥 VIDEO
            "video_engine": ModelConfig(
                name="ffmpeg_pipeline",
                type="video",
                local=True
            )
        }

    def get(self, key: str):
        return self.models[key]


registry = ModelRegistry()