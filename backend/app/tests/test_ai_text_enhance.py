import unittest
from unittest.mock import patch, AsyncMock

from app.api.v1.ai import enhance_text
from app.schemas.ai_schema import AITextEnhanceRequest


class TestAITextEnhance(unittest.IsolatedAsyncioTestCase):

    @patch('app.api.v1.ai.llm_client.generate', new_callable=AsyncMock)
    async def test_enhance_text_uses_json_mode(self, mock_generate):
        mock_generate.return_value = '{"title": "Enhanced Title", "topic": "Enhanced Topic"}'

        request = AITextEnhanceRequest(title="Hola", topic="Ideas cortas")
        response = await enhance_text(request)

        self.assertEqual(response.title, "Enhanced Title")
        self.assertEqual(response.topic, "Enhanced Topic")
        mock_generate.assert_awaited_once()
        self.assertTrue(mock_generate.call_args.kwargs.get('json_mode', False))
        self.assertEqual(mock_generate.call_args.kwargs.get('temperature'), 0.7)

    @patch('app.api.v1.ai.llm_client.generate', new_callable=AsyncMock)
    async def test_enhance_text_parses_json_with_extra_text(self, mock_generate):
        mock_generate.return_value = 'Here is your result:\n{"title": "Bright Title", "topic": "Exciting topic"}\nThank you.'

        request = AITextEnhanceRequest(title="Hola", topic="Ideas cortas")
        response = await enhance_text(request)

        self.assertEqual(response.title, "Bright Title")
        self.assertEqual(response.topic, "Exciting topic")
