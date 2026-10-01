from pathlib import Path
from PIL import Image
import io
from app.services.video_generator import VideoGenerator

base = Path('media/generated_images')
base.mkdir(parents=True, exist_ok=True)
for i, color in enumerate([(20, 50, 100), (80, 90, 140)]):
    p = base / f'test_image_{i}.png'
    if not p.exists():
        img = Image.new('RGB', (1024, 1024), color=color)
        img.save(p)

scenes = [
    {
        'text': 'A tranquil meadow with soft sunrise light',
        'duration': 4.0,
        'style': 'cctv',
        'platform': 'tiktok',
        'image_path': 'generated_images/test_image_0.png'
    },
    {
        'text': 'A stable portrait with warm, consistent lighting',
        'duration': 4.0,
        'style': 'cctv',
        'platform': 'tiktok',
        'image_path': 'generated_images/test_image_1.png'
    }
]

vg = VideoGenerator()
out = vg.assemble_video(scenes, 'integration_run_static_images.mp4')
print('OUTPUT', out)
