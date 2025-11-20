import os
import subprocess
import uuid
import json
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from sqlmodel import Session
from ..core.database import engine
from ..models.generated_video import GeneratedVideo

# Config
BASE_VIDEOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "videos"))
os.makedirs(BASE_VIDEOS_DIR, exist_ok=True)

# Ajustes del vídeo
WIDTH = 1080   # ancho 9:16
HEIGHT = 1920  # alto 9:16
FPS = 30

# Fuente (usa la que tengas instalada o coloca .ttf en resources)
DEFAULT_FONT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "resources", "Roboto-Regular.ttf"))
if not os.path.exists(DEFAULT_FONT_PATH):
    DEFAULT_FONT_PATH = None  # Pillow usará fuente por defecto


def _mk_frame_image(text: str, image_path: str, out_path: str):
    # Crear fondo
    img_width = 1080
    img_height = 1920

    if image_path:
        img = Image.open(image_path).convert("RGB").resize((img_width, img_height))
    else:
        img = Image.new("RGB", (img_width, img_height), color=(30, 30, 30))

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", size=60)

    # Ajustar texto multilinea
    max_width = img_width - 200
    lines = []
    words = text.split(" ")
    current = ""

    for word in words:
        test = current + " " + word if current else word

        # ✔️ textbbox() reemplaza a textsize()
        bbox = draw.textbbox((0, 0), test, font=font)
        w_width = bbox[2] - bbox[0]

        if w_width <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    lines.append(current)

    y = img_height - 400
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (img_width - text_width) / 2

        draw.text((x, y), line, font=font, fill="white")
        y += text_height + 10

    img.save(out_path)

def _create_video_from_frames(frames_dir: str, out_file: str, fps:int = FPS, music_file: str|None = None):
    """
    Usa ffmpeg para generar vídeo desde frames (frame0001.png ...).
    Añade pista de música si se proporciona (duplicando/parcheando duración).
    """
    # Crear vídeo desde frames
    input_pattern = os.path.join(frames_dir, "frame%05d.png")
    tmp_video = os.path.join(frames_dir, "tmp_video.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", input_pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={WIDTH}:{HEIGHT}",
        tmp_video
    ]
    subprocess.run(cmd, check=True)

    if music_file and os.path.exists(music_file):
        # mezclar audio: ajustar duración si la pista es más corta/larga
        # obtener duracion video
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                "default=noprint_wrappers=1:nokey=1", tmp_video], capture_output=True, text=True)
        video_dur = float(probe.stdout.strip() or 0.0)

        # crear audio cortado/loop si es necesario
        audio_tmp = os.path.join(frames_dir, "tmp_audio.mp3")
        # usar ffmpeg para loop/cortar: si audio más corto, loop; si más largo, trim
        cmd_audio = [
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", music_file, "-t", str(video_dur), "-c:a", "libmp3lame", audio_tmp
        ]
        subprocess.run(cmd_audio, check=True)

        # combinar video sin audio + audio tmp
        cmd_merge = [
            "ffmpeg", "-y",
            "-i", tmp_video,
            "-i", audio_tmp,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            out_file
        ]
        subprocess.run(cmd_merge, check=True)
    else:
        # renombrar tmp_video a out_file
        os.replace(tmp_video, out_file)

def assemble_video_from_scenes(scenes: List[Dict], output_filename: str|None = None, music_file: str|None = None) -> str:
    """
    scenes: lista de dicts con keys: text, duration (seg), image_prompt (opcional: ruta local o prompt)
    Devuelve la ruta del video generado.
    """
    uid = uuid.uuid4().hex[:8]
    if not output_filename:
        output_filename = f"video_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uid}.mp4"
    out_path = os.path.join(BASE_VIDEOS_DIR, output_filename)

    # crear carpeta temporal para frames
    tmp_dir = os.path.join(BASE_VIDEOS_DIR, f"tmp_{uid}")
    os.makedirs(tmp_dir, exist_ok=True)

    frame_index = 1
    try:
        for scene in scenes:
            text = scene.get("text", "")
            duration = int(scene.get("duration", 3))
            image_prompt = scene.get("image_prompt", None)
            # Si image_prompt apunta a archivo local válido, úsalo; si no, acepta None (placeholder)
            image_file = None
            if image_prompt and os.path.exists(image_prompt):
                image_file = image_prompt
            # generar N frames para esta escena (simple approach: repetir la misma imagen)
            n_frames = max(1, int(duration * FPS))
            frame_path = os.path.join(tmp_dir, f"frame{frame_index:05d}.png")
            _mk_frame_image(text=text, image_path=image_file, out_path=frame_path)
            frame_index += 1
            # duplicar frame para la duración (crear copias incrementales)
            for i in range(1, n_frames):
                src = frame_path
                dst = os.path.join(tmp_dir, f"frame{frame_index:05d}.png")
                Image.open(src).save(dst)
                frame_index += 1

        # crear vídeo desde frames
        _create_video_from_frames(tmp_dir, out_path, fps=FPS, music_file=music_file)
        return out_path

    finally:
        # opcional: limpiar tmp_dir
        try:
            for f in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, f))
            os.rmdir(tmp_dir)
        except Exception:
            pass

def generate_and_store_video(video_id: int, music_file: str|None = None):
    """
    Función de conveniencia: carga GeneratedVideo, llama al motor de IA si hace falta,
    genera el vídeo y actualiza la DB.
    """
    with Session(engine) as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            raise FileNotFoundError(f"GeneratedVideo {video_id} not found")
        # marca processing
        video.status = "processing"
        session.add(video)
        session.commit()
        session.refresh(video)

        # Suponemos que el campo topic y template_id existen. Para generar escenas usamos
        # endpoint AI interno o la lógica que tengas. Aquí simplificamos: llamaremos
        # al router AI local si necesitas, pero preferible que ya tengas guion en otra tabla.
        # Para prototipo: asumimos que 'video' tenga field 'scenes_json' (si no, genera con API)
        try:
            # Si existe scenes_json en video (opcional), úsala; sino llamar al endpoint AI
            scenes = []
            if hasattr(video, "scenes_json") and video.scenes_json:
                scenes = json.loads(video.scenes_json)
            else:
                # llamada local a la API ai para generar el guion (evita request de red)
                from ..api.v1.ai import generate_script  # función local; si tu ai router expone función reutilizable
                req = type("X", (), {"topic": video.topic, "template_id": video.template_id})
                ai_result = generate_script(req)  # devuelve AIScriptResponse
                scenes = [s.dict() for s in ai_result.scenes]

            # ensamblar vídeo
            out_path = assemble_video_from_scenes(scenes, music_file=music_file)
            # actualizar registro
            video.file_path = out_path
            video.status = "success"
            session.add(video)
            session.commit()
        except Exception as e:
            video.status = "error"
            session.add(video)
            session.commit()
            raise e
