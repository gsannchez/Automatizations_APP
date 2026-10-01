"""Similarity Engine service to avoid content duplicates and detect matching formats."""
import logging
from typing import List, Dict, Any
from sqlmodel import Session, select

from app.models.viral_intelligence import ContentEmbedding
from .clip_service import ClipService
from .semantic_search import SemanticSearch

logger = logging.getLogger(__name__)

class SimilarityEngine:
    """Detects content repetitiveness, matches similar templates, and avoids duplication."""
    
    def __init__(self, session: Session):
        self.session = session
        self.clip_service = ClipService()
        self.search_engine = SemanticSearch()
        
    def check_script_duplicate_ratio(self, script_text: str) -> float:
        """Verify if the script is highly similar to previously generated scripts in DB.
        
        Args:
            script_text: Full voiceover text.
            
        Returns:
            Highest similarity score found in DB (0.0 to 1.0).
        """
        logger.info("Checking script duplicate ratio in semantic memory...")
        query_vector = self.clip_service.get_text_embedding(script_text)
        
        # Pull all existing scene text embeddings from database
        stmt = select(ContentEmbedding).where(ContentEmbedding.entity_type == "scene_text")
        db_embeddings = self.session.exec(stmt).all()
        
        if not db_embeddings:
            return 0.0
            
        candidates = [
            {
                "id": str(db.id),
                "vector_data": db.vector_data
            }
            for db in db_embeddings
        ]
        
        results = self.search_engine.find_nearest_neighbors(query_vector, candidates, top_k=1)
        if results:
            return results[0]["similarity_score"]
        return 0.0
        
    def find_similar_assets(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find media assets or historical templates that match a textual query.
        
        Args:
            query_text: Plain text search query.
            top_k: Number of recommendations to return.
            
        Returns:
            Ranked list of similar assets or scenes from DB.
        """
        logger.info(f"Performing semantic search for similar assets: '{query_text}'")
        query_vector = self.clip_service.get_text_embedding(query_text)
        
        stmt = select(ContentEmbedding).where(ContentEmbedding.entity_type != "scene_text")
        db_embeddings = self.session.exec(stmt).all()
        
        if not db_embeddings:
            return []
            
        candidates = [
            {
                "id": str(db.id),
                "entity_id": str(db.entity_id),
                "entity_type": db.entity_type,
                "vector_data": db.vector_data,
                "extra_metadata": db.extra_metadata
            }
            for db in db_embeddings
        ]
        
        return self.search_engine.find_nearest_neighbors(query_vector, candidates, top_k=top_k)
