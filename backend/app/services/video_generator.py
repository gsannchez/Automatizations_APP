import os
import subprocess
import uuid
import random
from typing import List, Dict
from datetime import datetime
from sqlmodel import Session
from PIL import Image, ImageDraw, ImageFont
import io

from ..core.database import sync_engine as engine
from ..models.generated_video import GeneratedVideo
from .image_generator import generate_images_for_scenes
from .tts_service import tts_service
from .storage import storage # Inject storage service

# =============================
#   CONFIG GLOBAL
# =============================

# BASE_VIDEOS_DIR eliminada a favor de storage service
WIDTH = 1080
HEIGHT = 1920
FPS = 30
# FONT_PATH debe ser relativo o gestionado por storage/recursos
# Por ahora intentamos usar una ruta relativa si existe, o fallback
FONT_PATH = "media/resources/fonts/Inter-Bold.ttf" 

class VideoGenerator:
    def __init__(self):
        pass

    def _get_audio_duration(self, audio_path: str) -> float:
        """Obtiene la duración del audio usando ffprobe."""
        # audio_path debe ser una ruta local accesible para ffprobe
        local_audio_path = storage.get_local_path(audio_path)
        
        cmd = [
            "ffprobe", 
            "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            local_audio_path
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
            # Intentar cargar fuente desde storage si es necesario, 
            # pero ImageFont.truetype suele requerir path local
            font_path = FONT_PATH
            if not os.path.exists(font_path):
                 # Fallback a sistema si no existe local
                 font_path = "arial.ttf"
            font = ImageFont.truetype(font_path, 60)
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

        # Guardar en buffer y subir a storage
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        storage.save(buf, output_path)

    def _create_scene_clip(self, image_path: str, audio_path: str, text: str, output_path: str):
        """
        Genera un clip de video para una escena usando FFmpeg.
        """
        # Resolver rutas locales para FFmpeg
        local_image_path = storage.get_local_path(image_path)
        local_audio_path = storage.get_local_path(audio_path)
        
        duration = self._get_audio_duration(audio_path)
        duration = max(duration, 3.0)
        
        # Generar overlay de texto (se guarda en storage)
        overlay_path = output_path.replace(".mp4", "_overlay.png")
        self._create_text_overlay(text, overlay_path)
        local_overlay_path = storage.get_local_path(overlay_path)

        # Efecto Ken Burns aleatorio
        zoom_effect = ""
        if random.choice([True, False]):
            zoom_effect = f"zoompan=z='min(zoom+0.0015,1.5)':d={int(duration*25)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}"
        else:
            zoom_effect = f"zoompan=z='if(lte(zoom,1.0),1.5,max(1.001,zoom-0.0015))':d={int(duration*25)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={WIDTH}x{HEIGHT}"

        # Salida temporal local para FFmpeg
        local_output_path = f"tmp_scene_{uuid.uuid4().hex}.mp4"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", local_image_path,
            "-i", local_overlay_path,
            "-i", local_audio_path,
            "-filter_complex",
            f"[0:v]{zoom_effect}[bg];[bg][1:v]overlay=0:0[v]",
            "-map", "[v]", "-map", "2:a",
            "-t", str(duration),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            local_output_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            # Subir resultado a storage y borrar temporal
            with open(local_output_path, "rb") as f:
                storage.save(f, output_path)
        finally:
            # Limpieza de temporales locales
            if os.path.exists(local_output_path):
                os.remove(local_output_path)
            # No borramos overlay_path de storage aquí por si se quiere debug, o se puede borrar
            # storage.delete(overlay_path)

    def assemble_video(self, scenes: List[Dict], output_filename: str = None) -> str:
        uid = uuid.uuid4().hex[:8]
        # Usamos rutas relativas para el storage "videos/tmp_..."
        tmp_dir_rel = f"videos/tmp_{uid}" 
        
        if not output_filename:
            output_filename = f"video_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uid}.mp4"
        
        final_output_rel = f"videos/{output_filename}"

        # 1. Generar imágenes
        # Devuelve rutas relativas en storage
        image_paths = generate_images_for_scenes(scenes)

        scene_clips = []

        # 2. Generar clips por escena
        for i, scene in enumerate(scenes):
            text = scene.get("text", "")
            
            # Generar audio TTS
            audio_filename = f"tts_{uid}_{i}.mp3"
            # Devuelve ruta relativa en storage
            audio_path = tts_service.generate_audio(text, audio_filename) 
            
            # CLIP PATH en storage
            clip_path_rel = f"{tmp_dir_rel}/scene_{i}.mp4"
            
            print(f"🎬 Rendering scene {i}...")
            self._create_scene_clip(image_paths[i], audio_path, text, clip_path_rel)
            scene_clips.append(clip_path_rel)

        # 3. Concatenar clips
        # FFmpeg concat requiere un archivo de texto. Lo creamos localmente temporalmente
        # pero necesitamos las rutas LOCALES de los clips (get_local_path)
        
        # Opcion A: Descargar todos los clips a local tmp (si es S3).
        # Opcion B: Si es local storage, usar rutas locales absolutas.
        
        concat_list_path_local = f"concat_list_{uid}.txt"
        
        try:
            with open(concat_list_path_local, "w") as f:
                for clip_rel in scene_clips:
                    local_path = storage.get_local_path(clip_rel)
                    # FFmpeg requiere rutas con barras normales o escapadas
                    safe_path = local_path.replace("\\", "/")
                    f.write(f"file '{safe_path}'\n")

            print("🔗 Concatenating scenes...")
            local_final_output = f"final_{uid}.mp4"
            
            cmd_concat = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_path_local,
                "-c", "copy",
                local_final_output
            ]
            subprocess.run(cmd_concat, check=True)
            
            # Subir resultado final a storage
            with open(local_final_output, "rb") as f:
                storage.save(f, final_output_rel)
                
            print(f"✅ Video generated: {final_output_rel}")
            
            # Limpieza local final
            if os.path.exists(local_final_output):
                os.remove(local_final_output)
                
        finally:
             if os.path.exists(concat_list_path_local):
                os.remove(concat_list_path_local)

        return final_output_rel

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
