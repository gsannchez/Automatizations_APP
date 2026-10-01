import logging
import uuid
from uuid import UUID

from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.video_job_service import VideoJobService
from .utils import update_video_status
from .task_helpers import raise_or_retry

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.audio_generation.generate_audio_task", bind=True, max_retries=3)
def generate_audio_task(self, video_id_str: str, scene_idx: int):
    video_id = UUID(video_id_str)
    
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str
            
        update_video_status(session, video, PipelineState.AUDIO_GENERATION.value, progress=55)
            
        scenes = video.scenes_data
        scene_prog = video.scene_progress or {}
        idx = str(scene_idx)
        
        if scene_prog.get(idx, {}).get("audio") == "done":
            logger.info(f"⏭️ Escena {scene_idx} - Audio ya generado. Omitiendo.")
            return video_id_str
            
        job_service = VideoJobService(session)
        job = job_service.create_job(video_id, PipelineState.AUDIO_GENERATION.value)

        try:
            import asyncio
            from app.services.tts.elevenlabs_tts import ElevenLabsTTS
            from app.services.tts.voice_registry import VoiceRegistry
            
            scene = scenes[scene_idx]
            text = (
                scene.get("voiceover_text")
                or scene.get("text")
                or scene.get("narration")
                or ""
            )
            if not text.strip():
                text = f"Scene {scene_idx + 1}"
            character = scene.get("character", "narrator")
            style = scene.get("emotion", "neutral")
            
            logger.info(f"🗣️ Generando audio para escena {scene_idx} con ElevenLabs (Char: {character})...")
            
            tts = ElevenLabsTTS()
            registry = VoiceRegistry()
            voice_data = registry.get_voice(character)
            
            audio_path = asyncio.run(
                tts.generate_audio(
                    text=text, 
                    voice_id=voice_data["voice_id"], 
                    style=style
                )
            )
            
            from app.utils.media_utils import get_audio_duration
            duration = get_audio_duration(audio_path)
            
            scene["audio_path"] = audio_path
            scene["duration"] = duration
            scene["status"] = "AUDIO_GENERATED"
            scene_prog.setdefault(idx, {})
            scene_prog[idx]["audio"] = "done"
            
            video.scenes_data = scenes
            video.scene_progress = scene_prog
            session.add(video)
            session.commit()
            job_service.mark_success(job.id)
            
            logger.info(f"✅ Audio generado para escena {scene_idx} | Path: {audio_path} | Dur: {duration}s")
            return video_id_str
            
        except Exception as exc:
            job_service.mark_failure(job.id, str(exc))
            logger.error(f"❌ Error en audio escena {scene_idx}: {exc}")
            raise_or_retry(self, exc, countdown=15)
            
@celery_app.task(name="app.tasks.audio_generation.audio_complete_callback", bind=True)
def audio_complete_callback(self, video_id_str: str, results=None):
    logger.info("All audio completed for video %s", video_id_str)
    return video_id_str
