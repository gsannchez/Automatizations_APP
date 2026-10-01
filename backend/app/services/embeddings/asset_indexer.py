"""Asset indexing service to store embeddings in database."""
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlmodel import Session, select

from app.models.viral_intelligence import ContentEmbedding
from .clip_service import ClipService

logger = logging.getLogger(__name__)

class AssetIndexer:
    """Handles generating and persisting embeddings for various database entities."""
    
    def __init__(self, session: Session):
        self.session = session
        self.clip_service = ClipService()
        
    def index_scene_text(self, video_id: UUID, scene_index: int, text: str) -> ContentEmbedding:
        """Generate and save the embedding for a single video scene narration text.
        
        Args:
            video_id: UUID of the GeneratedVideo.
            scene_index: The numerical index of the scene.
            text: The voiceover script line.
            
        Returns:
            The created ContentEmbedding record.
        """
        logger.info(f"Indexing scene text for video {video_id}, scene index {scene_index}...")
        vector = self.clip_service.get_text_embedding(text)
        
        # Check if already indexed
        stmt = select(ContentEmbedding).where(
            ContentEmbedding.entity_id == video_id,
            ContentEmbedding.entity_type == "scene_text",
            ContentEmbedding.extra_metadata["scene_index"].as_string() == str(scene_index)
        )
        record = self.session.exec(stmt).first()
        
        if not record:
            record = ContentEmbedding(
                entity_id=video_id,
                entity_type="scene_text",
                vector_data=vector,
                extra_metadata={
                    "scene_index": scene_index,
                    "text_length": len(text)
                }
            )
        else:
            record.vector_data = vector
            record.extra_metadata = {
                "scene_index": scene_index,
                "text_length": len(text)
            }
            
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
        
    def index_media_asset(self, asset_id: UUID, file_path: str, asset_type: str, extra_meta: Optional[Dict[str, Any]] = None) -> ContentEmbedding:
        """Generate and save embedding for a video/image media asset file.
        
        Args:
            asset_id: UUID of the Asset.
            file_path: File system storage location.
            asset_type: Type of asset ('image_generation', 'audio_generation').
            extra_meta: Optional additional metadata fields.
            
        Returns:
            The created ContentEmbedding record.
        """
        logger.info(f"Indexing media asset {asset_id} ({asset_type})...")
        
        # If it is an image, calculate visual embedding. Otherwise textual description mapping.
        if "image" in asset_type.lower():
            vector = self.clip_service.get_image_embedding(file_path)
        else:
            vector = self.clip_service.get_text_embedding(file_path)
            
        meta = extra_meta or {}
        meta["file_path"] = file_path
        
        record = ContentEmbedding(
            entity_id=asset_id,
            entity_type=f"asset_{asset_type}",
            vector_data=vector,
            extra_metadata=meta
        )
        
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
