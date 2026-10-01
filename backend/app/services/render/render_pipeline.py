import os
import subprocess
import uuid
from typing import List, Dict

from ..storage import storage
from ..captions.caption_generator import CaptionGenerator
from ..captions.caption_styles import CaptionStyleProfile
from ..audio.audio_mixer import AudioMixer
from ..audio.music_engine import MusicEngine
from ..timeline.scene_rebalancer import SceneRebalancer
from .scene_composer import SceneComposer
from .safe_ffmpeg import SafeFFmpeg
from .ffmpeg_validator import FFmpegValidator
from ..video_ai.hybrid_generator import HybridGenerator
from ..adaptive.adaptive_rendering import AdaptiveRendering
from ..adaptive.quality_manager import QualityManager
from ..monitoring.gpu_watchdog import GPUWatchdog
from ..logging.structured_logger import StructuredLogger

log = StructuredLogger(__name__)

class RenderPipeline:
    """
    Advanced FFmpeg Render Pipeline (Phase 5/6/6.5).
    Supports AI Video Clips, static images with motion, and full production hardening.
    """
    
    def __init__(self, tmp_dir: str = "tmp_render"):
        self.tmp_dir = tmp_dir
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, exist_ok=True)
            
        self.caption_gen = CaptionGenerator(tmp_dir)
        self.hybrid_gen = HybridGenerator()

    def _get_audio_duration(self, audio_path: str) -> float:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
        try:
            return float(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip())
        except:
            return 3.0

    def render(self, scenes: List[Dict], style: str = "tiktok_classic", output_filename: str = None, trace_id: str = None) -> str:
        uid = uuid.uuid4().hex[:8]
        trace_id = trace_id or StructuredLogger.new_trace_id()
        if not output_filename:
            output_filename = f"viral_video_{uid}.mp4"

        final_local_path = os.path.join(self.tmp_dir, output_filename)
        log.info("Starting render", trace_id=trace_id, style=style, output=output_filename)

        # --- Phase 6.5: Adaptive Quality ---
        # Downgrade quality if VRAM is too high before starting
        if not GPUWatchdog.is_safe_to_start():
            log.warning("VRAM too high — downgrading quality tier", trace_id=trace_id)
            QualityManager.downgrade()

        render_params = AdaptiveRendering.get_render_params()
        log.info("Quality tier", trace_id=trace_id, tier=QualityManager.get_tier().value, params=render_params)

        # 1. Timeline Rebalancing & Setup
        for s in scenes:
            local_aud = storage.get_local_path(s.get("audio_path"))
            s["local_audio"] = local_aud
            if "duration" not in s or s["duration"] <= 0:
                s["duration"] = self._get_audio_duration(local_aud)
            s["local_image"] = storage.get_local_path(s.get("image_path"))
            log.info(f"Timeline Engine | Scene {s.get('scene_id', 'X')} Duration: {s['duration']}s")

        # Phase 6: Hybrid AI Video (only if quality tier allows it)
        processed_scenes = []
        for i, s in enumerate(scenes):
            prompt = s.get("text", "Cinematic shot")
            emotion = s.get("emotion", "neutral")
            if render_params.get("allow_ai_video", True):
                hybrid_res = self.hybrid_gen.process_scene(i, s["local_image"], prompt, s["duration"], style, emotion)
                s["is_ai_video"] = hybrid_res["is_ai_video"]
                s["video_path"] = hybrid_res["video_path"]
            else:
                s["is_ai_video"] = False
                s["video_path"] = None
                log.info(f"Scene {i}: AI video skipped (quality tier SAFE_MODE/PERFORMANCE)", trace_id=trace_id)
            processed_scenes.append(s)

        rebalanced_scenes = SceneRebalancer.rebalance(processed_scenes, style)

        # 2. Build FFmpeg inputs and filter graph (AUDIO-FIRST TIMELINE)
        inputs = []
        filter_complex = ""
        concat_inputs = ""
        input_idx = 0

        for i, scene in enumerate(rebalanced_scenes):
            duration = scene["duration"]
            
            # Add video/image input
            if scene.get("is_ai_video") and scene.get("video_path"):
                inputs.extend(["-t", str(duration), "-i", scene["video_path"]])
                v_idx = input_idx
                input_idx += 1
                filter_complex += f"[{v_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v{i}]; "
            else:
                inputs.extend(["-loop", "1", "-t", str(duration), "-i", scene["local_image"]])
                v_idx = input_idx
                input_idx += 1
                scene_filter = SceneComposer.get_scene_filter(i, duration, style=style, sub_index=scene.get("sub_index", 0))
                filter_complex += f"[{v_idx}:v]format=yuv420p,{scene_filter}[v{i}]; "

            # Add audio input
            inputs.extend(["-t", str(duration), "-i", scene["local_audio"]])
            a_idx = input_idx
            input_idx += 1
            
            # Ensure mono -> stereo or consistent sample rate if needed, or just pass directly
            filter_complex += f"[{a_idx}:a]aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]; "
            
            concat_inputs += f"[v{i}][a{i}]"

        filter_complex += f"{concat_inputs}concat=n={len(rebalanced_scenes)}:v=1:a=1[v_concat][a_concat]; "

        music_path = MusicEngine.select_background_music(style)
        inputs.extend(["-i", music_path])
        m_idx = input_idx
        
        # Mix TTS tracks (a_concat) with Background Music
        filter_complex += f"[v_concat]format=yuv420p[outv]; "
        filter_complex += f"[{m_idx}:a]volume=0.15[bgm]; [a_concat][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"

        cmd = [
            "ffmpeg", "-y"
        ] + inputs + [
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-preset", render_params["preset"],
            "-crf", str(render_params["crf"]),
            "-r", str(render_params["fps"]),
            final_local_path
        ]

        # --- Phase 6.5: Validate before executing ---
        if not FFmpegValidator.validate_inputs(inputs):
            log.error("FFmpeg input validation failed — aborting render", trace_id=trace_id)
            return None

        log.info("Executing Safe FFmpeg", trace_id=trace_id)
        success = SafeFFmpeg.run(cmd, timeout=render_params.get("timeout", 600))

        if not success:
            log.error("FFmpeg render failed after recovery attempts", trace_id=trace_id)
            return None

        log.info("Render complete", trace_id=trace_id, output=final_local_path)
        return f"videos/{output_filename}"
