from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SocialMediaService(ABC):
    """Base class for social media platform integrations."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, str]:
        """Authenticate and return access tokens."""
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token."""
        pass
    
    @abstractmethod
    async def upload_video(self, video_path: str, metadata: Dict[str, Any]) -> str:
        """Upload video and return video ID."""
        pass
    
    @abstractmethod
    async def schedule_video(self, video_id: str, publish_time: str) -> bool:
        """Schedule video for future publication."""
        pass
    
    @abstractmethod
    async def get_analytics(self, video_id: str) -> Dict[str, Any]:
        """Get video analytics."""
        pass
