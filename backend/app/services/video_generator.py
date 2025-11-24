import os
import subprocess
import uuid
import random
from typing import List, Dict
from datetime import datetime
from sqlmodel import Session
from PIL import Image, ImageDraw, ImageFont

from ..core.database import engine
from ..models.generated_video import GeneratedVideo
from .image_generator import generate_images_for_scenes
from .tts_service import tts_service

# =============================
#   CONFIG GLOBAL
# =============================

BASE_VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "videos"))
os.makedirs(BASE_VIDEOS_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1920
FPS = 30
FONT_PATH = "C:/Windows/Fonts/arial.ttf"

class VideoGenerator:
    def __init__(self):
        pass

    def _get_audio_duration(self, audio_path: str) -> float:
        """Obtiene la duración del audio usando ffprobe."""
        cmd = [
            "ffprobe", 
            "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            audio_path
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            print(f"[ERROR] Could not get audio duration: {e}")
            return 5.0 # Fallback

    def _create_text_overlay(self, text: str, output_path: str):
        """Crea una imagen transparente con el texto superpuesto."""
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(FONT_PATH, 60)
        except:
            font = ImageFont.load_default()

        # Lógica simple de word wrap
        margin = 100
        max_width = WIDTH - (margin * 2)
        lines = []
        words = text.split()
        current_line = []

        for word in words:
            current_line.append(word)
            w = draw.textlength(" ".join(current_line), font=font)
            if w > max_width:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        # Dibujar fondo y texto
        text_height = len(lines) * 80
        start_y = HEIGHT - 500 - text_height
        
        # Caja negra semitransparente
        box_coords = [margin - 20, start_y - 20, WIDTH - margin + 20, start_y + text_height + 20]
        draw.rectangle(box_coords, fill=(0, 0, 0, 160))

        y = start_y
        for line in lines:
            # Sombra
            draw.text((margin + 2, y + 2), line, font=font, fill="black")
            # Texto
            draw.text((margin, y), line, font=font, fill="white")
            y += 80

        img.save(output_path)

    def _create_scene_clip(self, image_path: str, audio_path: str, text: str, output_path: str):
        """
        Genera un clip de video para una escena usando FFmpeg:
        - Imagen con efecto Zoompan (Ken Burns)
        - Audio sincronizado
        - Texto superpuesto
        """
        duration = self._get_audio_duration(audio_path)
        
        # Ajustar duración mínima para evitar errores de ffmpeg con clips muy cortos
        duration = max(duration, 3.0)
        
        # Generar overlay de texto
        overlay_path = output_path.replace(".mp4", "_overlay.png")
        self._create_text_overlay(text, overlay_path)

        # Efecto Ken Burns aleatorio (zoom in o zoom out)
        zoom_effect = ""
        if random.choice([True, False]):
            # Zoom In
            zoom_effect = f"zoompan=z='min(zoom+0.0015,1.5)':d={int(duration*25)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}"
        else:
            # Zoom Out (empezar en 1.5 y bajar)
            zoom_effect = f"zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))':d={int(duration*25)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}"

        # Comando FFmpeg complejo
        # 1. Imagen entrada -> Loop -> Zoompan -> Video Stream
        # 2. Audio entrada
        # 3. Overlay entrada
        # 4. Mezclar Video + Overlay
        # 5. Cortar a duración exacta del audio
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", image_path,
            "-i", overlay_path,
            "-i", audio_path,
            "-filter_complex",
            f"[0:v]{zoom_effect}[bg];[bg][1:v]overlay=0:0[v]",
            "-map", "[v]", "-map", "2:a",
            "-t", str(duration),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        
        # Limpiar overlay temporal
        if os.path.exists(overlay_path):
            os.remove(overlay_path)

    def assemble_video(self, scenes: List[Dict], output_filename: str = None) -> str:
        uid = uuid.uuid4().hex[:8]
        tmp_dir = os.path.join(BASE_VIDEOS_DIR, f"tmp_{uid}")
        os.makedirs(tmp_dir, exist_ok=True)

        if not output_filename:
            output_filename = f"video_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uid}.mp4"
        final_output_path = os.path.join(BASE_VIDEOS_DIR, output_filename)

        # 1. Generar imágenes
        image_paths = generate_images_for_scenes(scenes)

        scene_clips = []

        # 2. Generar clips por escena
        for i, scene in enumerate(scenes):
            text = scene.get("text", "")
            
            # Generar audio TTS
            audio_filename = f"tts_{uid}_{i}.mp3"
            audio_path = tts_service.generate_audio(text, audio_filename)
            
            clip_path = os.path.join(tmp_dir, f"scene_{i}.mp4")
            
            print(f"🎬 Rendering scene {i}...")
            self._create_scene_clip(image_paths[i], audio_path, text, clip_path)
            scene_clips.append(clip_path)

        # 3. Concatenar clips
        concat_list_path = os.path.join(tmp_dir, "concat_list.txt")
        with open(concat_list_path, "w") as f:
            for clip in scene_clips:
                # FFmpeg requiere rutas con barras normales o escapadas
                safe_path = clip.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        print("🔗 Concatenating scenes...")
        cmd_concat = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list_path,
            "-c", "copy",
            final_output_path
        ]
        subprocess.run(cmd_concat, check=True)

        print(f"✅ Video generated: {final_output_path}")
        return final_output_path

# Wrapper para compatibilidad con el código existente en main.py/api
def generate_and_store_video(video_id: int):
    with Session(engine) as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            raise FileNotFoundError()

        video.status = "processing"
        session.add(video)
        session.commit()

        try:
            from ..api.v1.ai import generate_script
            from ..schemas.ai_schema import AIScriptRequest
            
            # Simular request
            req = AIScriptRequest(
                topic=video.topic, 
                template_id=video.template_id,
                platform="TikTok" # Default por ahora, se podría sacar de DB
            )
            
            result = generate_script(req)
            scenes = [s.dict() for s in result.scenes]

            generator = VideoGenerator()
            out_path = generator.assemble_video(scenes)

            video.file_path = out_path
            video.status = "success"
            session.add(video)
            session.commit()

        except Exception as e:
            print(f"❌ Error generating video: {e}")
            video.status = "error"
            session.add(video)
            session.commit()
            raise e
