import unittest
from unittest.mock import patch, MagicMock
from app.services.script_generator import ScriptGenerator
from app.schemas.ai_schema import AIScriptRequest
from app.models.template import Template

from fastapi import HTTPException

class TestScriptGenerator(unittest.TestCase):

    @patch('app.services.script_generator.generate_gemini_prompt')
    def test_generate_script_success(self, mock_generate):
        # Mock response from Gemini
        mock_response = """
        [
            {
                "text": "Welcome to the future.",
                "duration": 5,
                "image_prompt": "Futuristic city, neon lights"
            },
            {
                "text": "AI is changing everything.",
                "duration": 4,
                "image_prompt": "Robot shaking hands with human"
            }
        ]
        """
        mock_generate.return_value = mock_response

        # Input data
        request_data = AIScriptRequest(
            topic="AI Future",
            template_id=1,
            tone="Exciting",
            platform="YouTube",
            language="English"
        )
        
        template = Template(
            id=1,
            name="Test Template",
            structure_json='[{"section": "Intro", "duration": 5}]'
        )

        # Execute
        generator = ScriptGenerator()
        response = generator.generate(request_data, template)

        # Verify
        self.assertEqual(len(response.scenes), 2)
        self.assertEqual(response.scenes[0].text, "Welcome to the future.")
        self.assertEqual(response.scenes[0].duration, 5)
        
        # Verify prompt construction (partial check)
        args, _ = mock_generate.call_args
        prompt_sent = args[0]
        self.assertIn("AI Future", prompt_sent)
        self.assertIn("YouTube", prompt_sent)
        self.assertIn("Exciting", prompt_sent)

    @patch('app.services.script_generator.generate_gemini_prompt')
    def test_generate_script_invalid_json(self, mock_generate):
        # Mock invalid response
        mock_generate.return_value = "I am not a JSON"

        request_data = AIScriptRequest(topic="Test", template_id=1)
        template = Template(id=1, name="T", structure_json="[]")

        generator = ScriptGenerator()
        
        with self.assertRaises(HTTPException):
            generator.generate(request_data, template)

if __name__ == '__main__':
    unittest.main()
