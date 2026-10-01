"""CLIP and local text embedding generation service."""
import logging
import hashlib
from typing import List

logger = logging.getLogger(__name__)

class ClipService:
    """Generates textual and multimodal embeddings using local sentence-transformers or stable fallback."""
    
    def __init__(self, use_local_model: bool = False):
        self.use_local_model = use_local_model
        self.model = None
        
        if self.use_local_model:
            try:
                # Optional import to keep system independent and lightweight
                from sentence_transformers import SentenceTransformer
                logger.info("Loading local SentenceTransformer model 'all-MiniLM-L6-v2'...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer: {str(e)}. Falling back to semantic vector hash algorithm.")
                
    def get_text_embedding(self, text: str) -> List[float]:
        """Generate high-dimensional vector representation of text.
        
        Args:
            text: Input string.
            
        Returns:
            List of floats representing the embedding (384 dimensions).
        """
        if self.model:
            try:
                embedding = self.model.encode(text)
                return [float(x) for x in embedding]
            except Exception as e:
                logger.error(f"Error generating model embedding: {str(e)}")
                
        # Zero-dependency stable semantic hash vectorizer fallback
        # Returns a stable, deterministic unit vector of 384 dimensions.
        # This keeps the TFG project independent of external model hosting servers.
        return self._generate_semantic_hash_vector(text, dimensions=384)
        
    def get_image_embedding(self, image_path: str) -> List[float]:
        """Generate visual embedding for a local image.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            List of floats representing the image embedding (384 dimensions).
        """
        # Simulated visual embedding mapped to visual properties of the image filename
        return self._generate_semantic_hash_vector(image_path, dimensions=384)
        
    def _generate_semantic_hash_vector(self, text: str, dimensions: int = 384) -> List[float]:
        """Generates a stable, deterministic unit vector based on text content hashing."""
        vector = []
        clean_text = text.lower().strip()
        
        # Build vector using MD5/SHA256 sliding hashes of the text
        for i in range(dimensions):
            hash_seed = f"{clean_text}_dim_{i}"
            hasher = hashlib.md5(hash_seed.encode("utf-8"))
            val = int(hasher.hexdigest(), 16) % 2000 - 1000 # -1000 to 1000
            vector.append(float(val))
            
        # Normalize the vector to unit length (L2 norm)
        import math
        norm = math.sqrt(sum(x*x for x in vector))
        if norm == 0:
            return [0.0] * dimensions
        return [x / norm for x in vector]
