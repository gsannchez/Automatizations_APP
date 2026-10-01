"""Hook Generator service to automatically rewrite script openings for high engagement."""
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HookGenerator:
    """Provides semantic rewriting of boring/standard opening sentences into viral ganchos."""
    
    VIRAL_TEMPLATES = [
        "Las cámaras captaron el momento exacto en el que {subject} hizo algo totalmente imposible.",
        "Hay una razón de peso por la que prohibieron hablar de esto sobre {subject}...",
        "Nadie esperaba lo que este {subject} estaba a punto de descubrir...",
        "Lo que encontraron enterrado bajo {subject} ha dejado a todos sin palabras.",
        "Esto es lo que pasa realmente cuando intentas desafiar a {subject}...",
        "El misterioso incidente de {subject} que intentaron ocultarte..."
    ]
    
    def rewrite_opening(self, original_opening: str) -> str:
        """Analyze a weak opening line and generate a highly dramatic, viral alternative.
        
        Args:
            original_opening: The original boring script opening.
            
        Returns:
            The improved viral hook.
        """
        logger.info(f"Rewriting hook: '{original_opening}'")
        text_lower = original_opening.lower()
        
        # Simple extraction of key subjects/nouns from the original sentence
        # (e.g. un perro, una cabaña, la tecnología, la historia)
        subject = "esto"
        
        # Heuristics to extract a good subject
        keywords = ["perro", "cabaña", "cámara", "secreto", "historia", "gobierno", "accidente", "tesoro", "objeto"]
        for key in keywords:
            if key in text_lower:
                subject = f"este {key}"
                break
                
        # If no specific key is matched, try looking for general nouns/pronouns
        if subject == "esto":
            words = original_opening.split()
            if len(words) > 1:
                # Use the last few words or key words
                subject = " ".join(words[-2:]).strip(".,?!")
                
        # Format a random template based on subject length to give deterministic variety
        template_idx = len(subject) % len(self.VIRAL_TEMPLATES)
        viral_hook = self.VIRAL_TEMPLATES[template_idx].format(subject=subject)
        
        return viral_hook
