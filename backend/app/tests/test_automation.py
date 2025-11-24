import unittest
from unittest.mock import patch, MagicMock
from app.core.scheduler import start_scheduler, stop_scheduler, scheduler
from app.tasks import generate_video_task

class TestAutomation(unittest.TestCase):

    @patch('app.core.scheduler.scheduler')
    def test_scheduler_lifecycle(self, mock_scheduler):
        # Setup mock state
        mock_scheduler.running = False
        
        # Test start
        start_scheduler()
        mock_scheduler.start.assert_called_once()
        
        # Simulate running state
        mock_scheduler.running = True
        
        # Test stop
        stop_scheduler()
        mock_scheduler.shutdown.assert_called_once()

    @patch('app.tasks.generate_and_store_video')
    def test_celery_task_execution(self, mock_generate):
        # Test calling the task function directly (synchronously)
        # Celery tasks are just functions wrapped in a Task object
        
        # Mock successful execution
        result = generate_video_task.apply(args=[123]).get()
        
        self.assertEqual(result, "Video 123 generated successfully.")
        mock_generate.assert_called_with(123)

if __name__ == '__main__':
    unittest.main()
