"""Emotional Intensity analyzer for script suspense and engagement triggers."""
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EmotionalIntensity:
    """Measures psychological tension, curiosity gap, and emotional load."""
    
    TENSION_WORDS = [
        "aterrador", "misterioso", "peligro", "secreto", "oscuro", "ilegal", "prohibido",
        "pánico", "oculto", "shocks", "impactante", "extraño", "inexplicable", "imposible",
        "escalofriante", "miedo", "tumba", "cámara", "captó", "misterio", "secreto", "suspenso"
    ]
    
    URGENCY_WORDS = [
        "ahora", "urgente", "alerta", "última hora", "cuidado", "atención", "espera", "mira esto",
        "inmediatamente", "rápido", "nunca", "siempre", "hoy", "grave", "crítico", "peligroso"
    ]
    
    PAYOFF_WORDS = [
        "reveló", "descubrió", "finalmente", "entonces", "aquí está", "resultado", "conclusión",
        "por fin", "mira el final", "resolución", "explicación", "verdad", "demostró"
    ]
    
    def analyze_emotions(self, script_text: str) -> Dict[str, Any]:
        """Examine the emotional dictionary and syntax of the script.
        
        Args:
            script_text: Full voiceover text.
            
        Returns:
            Dict containing emotional_intensity, curiosity_gap, and keyword counts.
        """
        if not script_text:
            return {"emotional_intensity": 0.0, "curiosity_gap": 0.0}
            
        text_lower = script_text.lower()
        words = text_lower.split()
        total_words = len(words)
        
        if total_words == 0:
            return {"emotional_intensity": 0.0, "curiosity_gap": 0.0}
            
        # Count words matches
        tension_count = sum(1 for w in words if any(t in w for t in self.TENSION_WORDS))
        urgency_count = sum(1 for w in words if any(u in w for u in self.URGENCY_WORDS))
        payoff_count = sum(1 for w in words if any(p in w for p in self.PAYOFF_WORDS))
        
        # Calculate density
        tension_density = tension_count / total_words
        urgency_density = urgency_count / total_words
        
        # Emotional Intensity Score
        # High density of tension and urgency words raise emotional intensity
        emo_score = min((tension_density * 8.0) + (urgency_density * 4.0) + 0.15, 1.0)
        
        # Curiosity Gap Score
        # Suspense is high when tension matches a lack of immediate payoff or clear mystery structure
        curiosity_score = min((tension_density * 10.0) + (0.1 if payoff_count > 0 else 0.35), 1.0)
        
        return {
            "emotional_intensity": round(emo_score, 2),
            "curiosity_gap": round(curiosity_score, 2),
            "tension_keywords_found": tension_count,
            "urgency_keywords_found": urgency_count,
            "payoff_keywords_found": payoff_count
        }
