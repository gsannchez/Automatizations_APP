"""Semantic search and cosine similarity engine."""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SemanticSearch:
    """Provides fast cosine-similarity comparisons for high-dimensional embeddings."""
    
    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity score between two float vectors.
        
        Args:
            vec_a: First float vector.
            vec_b: Second float vector.
            
        Returns:
            Cosine similarity score (0.0 to 1.0).
        """
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a)
        norm_b = sum(b * b for b in vec_b)
        
        import math
        denominator = math.sqrt(norm_a) * math.sqrt(norm_b)
        if denominator == 0:
            return 0.0
            
        similarity = dot_product / denominator
        # Standardize range between 0.0 and 1.0 (since visual/text vectors can have negative values)
        return (similarity + 1.0) / 2.0
        
    def find_nearest_neighbors(self, query_vector: List[float], candidates: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Rank candidates by cosine similarity relative to the query vector.
        
        Args:
            query_vector: The search query embedding vector.
            candidates: List of dicts representing candidates. Must contain a 'vector_data' key.
            top_k: Number of results to return.
            
        Returns:
            Ranked list of candidates with an added 'score' field.
        """
        scored_candidates = []
        for candidate in candidates:
            cand_vector = candidate.get("vector_data")
            if not cand_vector:
                continue
                
            score = self.cosine_similarity(query_vector, cand_vector)
            scored_candidates.append({
                **candidate,
                "similarity_score": round(score, 4)
            })
            
        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_candidates[:top_k]
