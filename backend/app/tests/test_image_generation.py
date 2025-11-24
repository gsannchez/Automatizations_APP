import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
from app.services.automatic1111_client import Automatic1111Client
from app.services.image_generator import ImageGenerator

class TestImageGeneration(unittest.TestCase):

    def setUp(self):
        # Crear directorio temporal para tests
        self.test_dir = "generated_images"
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        # Limpiar archivos generados (opcional, cuidado en dev)
        # shutil.rmtree(self.test_dir) 
        pass

    @patch('app.services.automatic1111_client.requests.post')
    def test_a1111_client_payload(self, mock_post):
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"images": ["VGhpcyBpcyBhIHRlc3Q="]} # "This is a test" in b64
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = Automatic1111Client()
        result = client.generate_image(prompt="test prompt", steps=50)

        self.assertIsNotNone(result)
        
        # Verificar payload
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['prompt'], "test prompt")
        self.assertEqual(payload['steps'], 50)
        self.assertIn("bad quality", payload['negative_prompt']) # Default negative prompt

    @patch('app.services.automatic1111_client.Automatic1111Client.generate_image')
    def test_image_generator_caching(self, mock_generate):
        # Mock generate to return dummy bytes
        mock_generate.return_value = b"fake_image_data"

        generator = ImageGenerator()
        scenes = [{"image_prompt": "unique prompt for cache test"}]

        # Primera ejecución: debe llamar a generate_image
        paths1 = generator.generate_images_for_scenes(scenes)
        self.assertTrue(mock_generate.called)
        self.assertEqual(mock_generate.call_count, 1)
        
        # Reset mock
        mock_generate.reset_mock()

        # Segunda ejecución: NO debe llamar a generate_image (usar caché)
        paths2 = generator.generate_images_for_scenes(scenes)
        self.assertFalse(mock_generate.called)
        self.assertEqual(paths1, paths2)

        # Limpieza
        if os.path.exists(paths1[0]):
            os.remove(paths1[0])

if __name__ == '__main__':
    unittest.main()
