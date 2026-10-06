"""Contract tests for the async video endpoints.

These lock the two things the Angular frontend depends on:
  * a freshly created video reports status ``QUEUED`` (its progress comes from
    the ``progress`` fallback, not a stored column), and
  * POST /videos/{id}/generate queues the orchestrator with the *string* id.
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.api.v1.videos import create_video, generate_video_endpoint
from app.models.generated_video import GeneratedVideo
from app.models.user import User
from app.schemas.generated_video_schema import GeneratedVideoCreate


def _user() -> User:
    return User.model_construct(id=uuid4())


class TestAsyncAPI(unittest.IsolatedAsyncioTestCase):

    async def test_create_video(self):
        mock_session = AsyncMock()

        data = GeneratedVideoCreate(
            topic="Test Topic",
            title="Test Video",
            platform="TIKTOK",
            template_id=uuid4(),
        )

        result = await create_video(data, session=mock_session, current_user=_user())

        self.assertEqual(result.topic, "Test Topic")
        self.assertEqual(result.title, "Test Video")
        self.assertEqual(result.status, "QUEUED")
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch("app.api.v1.videos.process_video_workflow")
    async def test_generate_video_endpoint(self, mock_workflow):
        video_id = uuid4()
        mock_video = GeneratedVideo.model_construct(id=video_id, status="DONE")

        # _get_owned_video does: result = await session.execute(...) then
        # result.scalars().first()
        result_proxy = MagicMock()
        result_proxy.scalars.return_value.first.return_value = mock_video

        mock_session = AsyncMock()
        mock_session.execute.return_value = result_proxy

        response = await generate_video_endpoint(
            video_id=video_id, session=mock_session, current_user=_user()
        )

        # The endpoint resets the row to QUEUED before handing off to Celery.
        self.assertEqual(mock_video.status, "QUEUED")
        self.assertIn("Celery", response["message"])
        self.assertEqual(response["video_id"], str(video_id))
        mock_workflow.delay.assert_called_once_with(str(video_id))


if __name__ == "__main__":
    unittest.main()
