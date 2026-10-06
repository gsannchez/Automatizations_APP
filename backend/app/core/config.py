from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Auto Video Maker"

    # Database configuration
    DATABASE_URL: str = "postgresql://autovideouser:autovideopass@localhost:5432/autovideodb"

    # Storage configuration
    STORAGE_TYPE: str = "local"  # local or s3

    # ------------------------------------------------------------------
    # LLM (script generation)
    # ------------------------------------------------------------------
    # "auto"      -> Gemini when a key is available, else local Ollama
    # "gemini"    -> force Gemini
    # "ollama"    -> force local Ollama
    LLM_PROVIDER: str = "auto"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    LOCAL_LLM_URL: str = "http://localhost:11434"
    LOCAL_LLM_MODEL: str = "qwen2.5:7b-instruct"

    # ------------------------------------------------------------------
    # Image generation (ComfyUI)
    # ------------------------------------------------------------------
    COMFYUI_ENABLED: bool = True
    COMFYUI_URL: str = "http://127.0.0.1:8188"
    COMFYUI_CHECKPOINT: str = "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"
    COMFYUI_SCENE_TIMEOUT_SECONDS: int = 600

    # ------------------------------------------------------------------
    # Video generation (local GPU — Stable Video Diffusion)
    # ------------------------------------------------------------------
    VIDEO_BACKEND: str = "svd"  # svd | animatediff | ffmpeg
    SVD_MODEL_ID: str = "stabilityai/stable-video-diffusion-img2vid-xt-1-1"
    SVD_NUM_FRAMES: int = 25
    SVD_FPS: int = 7
    SVD_DECODE_CHUNK_SIZE: int = 2
    SVD_CPU_OFFLOAD: bool = True
    HF_TOKEN: str | None = None

    # ------------------------------------------------------------------
    # TTS
    # ------------------------------------------------------------------
    TTS_PROVIDER: str = "gtts"  # gtts | elevenlabs
    ELEVENLABS_API_KEY: str | None = None
    TTS_LANGUAGE: str = "es"  # default narration language (gTTS lang code)

    # ------------------------------------------------------------------
    # Assembly / post-production
    # ------------------------------------------------------------------
    MUSIC_BED_PATH: str | None = None
    SUBTITLE_ENABLED: bool = True
    VIDEO_WIDTH: int = 1080
    VIDEO_HEIGHT: int = 1920
    VIDEO_FPS: int = 30

    # ------------------------------------------------------------------
    # Redis / Celery
    # ------------------------------------------------------------------
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # ------------------------------------------------------------------
    # Startup recovery
    # ------------------------------------------------------------------
    VIDEO_STARTUP_REQUEUE: bool = False
    VIDEO_STARTUP_MARK_STUCK_FAILED: bool = False
    VIDEO_STUCK_FAILED_MINUTES: int = 30

    # JWT authentication
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30          # short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7             # long-lived refresh token

    class Config:
        env_file = ".env"


settings = Settings()


def use_comfyui() -> bool:
    """Whether ComfyUI is the active image backend.

    Exposed as a function (not a plain setting) because ``services/comfyui_health``
    imports it by name.
    """
    return settings.COMFYUI_ENABLED
