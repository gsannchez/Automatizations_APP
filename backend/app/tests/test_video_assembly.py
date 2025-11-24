import unittest
from unittest.mock import patch, MagicMock
import os
from app.services.tts_service import TTSService
from app.services.video_generator import VideoGenerator

class TestVideoAssembly(unittest.TestCase):

    def setUp(self):
        self.test_dir = "generated_audio"
        os.makedirs(self.test_dir, exist_ok=True)

    @patch('app.services.tts_service.gTTS')
    def test_tts_generation(self, mock_gtts):
        # Mock gTTS save
        mock_instance = MagicMock()
        mock_gtts.return_value = mock_instance
        
        service = TTSService()
        path = service.generate_audio("Hello world", "test_audio.mp3")
        
        self.assertTrue(os.path.exists(path) or path.endswith("test_audio.mp3"))
        mock_instance.save.assert_called_once()

    @patch('app.services.video_generator.subprocess.run')
    @patch('app.services.video_generator.generate_images_for_scenes')
    @patch('app.services.video_generator.tts_service.generate_audio')
    def test_video_assembly_flow(self, mock_tts, mock_images, mock_subprocess):
        # Mocks
        mock_images.return_value = ["img1.png", "img2.png"]
        mock_tts.return_value = "audio.mp3"
        
        # Mock subprocess for ffprobe (duration) and ffmpeg
        # First call is ffprobe (twice, once per scene), then ffmpeg (twice), then concat
        # We need to handle the return values carefully
        
        def side_effect(*args, **kwargs):
            cmd = args[0]
            if cmd[0] == "ffprobe":
                mock_res = MagicMock()
                mock_res.stdout = "5.0"
                return mock_res
            return MagicMock()

        mock_subprocess.side_effect = side_effect

        scenes = [
            {"text": "Scene 1", "duration": 5},
            {"text": "Scene 2", "duration": 5}
        ]

        generator = VideoGenerator()
        out_path = generator.assemble_video(scenes, "test_video.mp4")

        self.assertTrue("test_video.mp4" in out_path)
        
        # Verify calls
        # 2 scenes -> 2 ffprobe calls + 2 ffmpeg clip calls + 1 ffmpeg concat call = 5 calls
        self.assertEqual(mock_subprocess.call_count, 5)

if __name__ == '__main__':
    unittest.main()
