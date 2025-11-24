import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from app.api.v1.videos import create_video, generate_video_endpoint
from app.schemas.generated_video_schema import GeneratedVideoCreate
from app.models.generated_video import GeneratedVideo

class TestAsyncAPI(unittest.IsolatedAsyncioTestCase):

    async def test_create_video(self):
        # Mock AsyncSession
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        data = GeneratedVideoCreate(topic="Test Topic", template_id=1)
        
        # Call endpoint
        result = await create_video(data, session=mock_session)
        
        self.assertEqual(result.topic, "Test Topic")
        self.assertEqual(result.status, "pending")
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch('app.api.v1.videos.generate_video_task')
    async def test_generate_video_endpoint(self, mock_task):
        # Mock AsyncSession
        mock_session = AsyncMock()
        mock_session.get = AsyncMock()
        mock_session.commit = AsyncMock()
        
        # Mock existing video
        mock_video = GeneratedVideo(id=1, topic="Test", template_id=1, status="pending")
        mock_session.get.return_value = mock_video
        
        # Call endpoint
        response = await generate_video_endpoint(video_id=1, session=mock_session)
        
        self.assertEqual(response["message"], "Video generation queued via Celery")
        self.assertEqual(mock_video.status, "queued")
        
        # Verify Celery task call
        mock_task.delay.assert_called_with(1)

if __name__ == '__main__':
    unittest.main()
