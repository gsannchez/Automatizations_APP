class BaseProvider:
    """
    Abstract base class for Cloud AI Video providers.
    """
    def generate(self, prompt: str, image_path: str, duration: float) -> str:
        raise NotImplementedError("Cloud providers must implement generate()")
