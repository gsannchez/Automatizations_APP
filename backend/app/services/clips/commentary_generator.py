"""Commentary Generator service for automated clip narrations."""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CommentaryGenerator:
    """Generates engaging subtitle narratives or voiceover commentaries for selected highlight clips."""
    
    TONE_TEMPLATES = {
        "tension": [
            "Fíjate en este detalle. Nadie esperaba lo que pasaría un segundo después...",
            "La tensión en esta escena es insoportable. Presten atención al fondo...",
            "Aquí es exactamente donde todo cambió. El misterio finalmente se revela..."
        ],
        "shock": [
            "¡No vas a creer lo que acaba de suceder aquí! Míralo de nuevo.",
            "Esto ha dejado sin palabras a todos los espectadores del mundo.",
            "¡El momento exacto en el que ocurre lo imposible!"
        ],
        "humor": [
            "POV: Cuando crees que tienes todo bajo control y pasa esto...",
            "La mejor parte de todo el video es esta, sin duda alguna.",
            "¡El final más inesperado de todos los tiempos!"
        ],
        "neutral": [
            "Analicemos detalladamente los sucesos que ocurren en esta escena.",
            "Esta secuencia representa el punto de inflexión del metraje.",
            "A continuación veremos el desarrollo de los acontecimientos principales."
        ]
    }
    
    def generate_commentary(self, clip_text: str, tone: str = "neutral") -> str:
        """Create a short, dramatic reaction commentary to overlay on the clip.
        
        Args:
            clip_text: Original transcript of the clip.
            tone: Emotional tone of the clip ('tension', 'shock', 'humor', 'neutral').
            
        Returns:
            The generated commentary text.
        """
        logger.info(f"Generating clip commentary with tone: {tone}...")
        
        templates = self.TONE_TEMPLATES.get(tone.lower(), self.TONE_TEMPLATES["neutral"])
        
        # Pick a template deterministically
        seed = len(clip_text)
        template_idx = seed % len(templates)
        template = templates[template_idx]
        
        # If there's original transcript, combine them
        if clip_text:
            # First few words of transcript to contextualize
            words = clip_text.split()
            snippet = " ".join(words[:12])
            return f"{template} Como se escucha en el audio: '{snippet}...'"
            
        return template
