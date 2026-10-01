from .base_provider import BaseProvider

class RunwayProvider(BaseProvider):
    """
    Integration for Runway Gen-2 / Gen-3 Alpha API.
    To be implemented when API access is configured.
    """
    def generate(self, prompt: str, image_path: str, duration: float) -> str:
        print(f"[Runway] Requesting generation for {image_path}...")
        # TODO: Implement actual API call to Runway ML
        return "videos/runway_mock.mp4"
