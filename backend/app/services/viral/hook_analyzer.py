"""Hook Analyzer service for evaluating script opening hook strength."""
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class HookAnalyzer:
    """Evaluates opening lines of a script to estimate psychological hook strength."""
    
    VIRAL_HOOK_TRIGGERS = [
        r"(nadie|ninguno|ninguna) (esperaba|sabía|te dirá|te cuenta)",
        r"lo que (encontraron|vieron|descubrieron|pasó realmente)",
        r"hay una razón (por la que|de por qué)",
        r"(prohibieron|ocultaron|cerraron|clausuraron) esto",
        r"el misterio de",
        r"(no vas a|nunca vas a) creer",
        r"las cámaras (captaron|grabaron)",
        r"el momento exacto en",
        r"esto es lo que pasa cuando",
        r"este es el secreto mejor guardado",
        r"por esto el gobierno",
        r"el misterioso incidente",
        r"nunca te dijeron esto sobre"
    ]
    
    def analyze_hook(self, script_text: str) -> Dict[str, Any]:
        """Analyze the first 30-50 words of a script representing the hook phase.
        
        Args:
            script_text: Full voiceover script.
            
        Returns:
            Dict containing hook_score (0.0 to 1.0) and identified_patterns.
        """
        if not script_text:
            return {"hook_score": 0.0, "patterns": [], "feedback": "Script is empty."}
            
        # Extract first 150 characters or first sentence as the hook
        sentences = re.split(r'[.!?]', script_text)
        first_few = " ".join(sentences[:2]).strip()
        
        matched_triggers = []
        score_boost = 0.0
        
        # Check against regex triggers
        for trigger in self.VIRAL_HOOK_TRIGGERS:
            match = re.search(trigger, first_few.lower())
            if match:
                matched_triggers.append(match.group(0))
                score_boost += 0.35
                
        # Additional checks
        # Punctuation check (exclamation or question raises curiosity)
        has_question = "?" in first_few
        has_exclamation = "!" in first_few
        
        if has_question:
            score_boost += 0.15
        if has_exclamation:
            score_boost += 0.10
            
        # Word count check (short, punchy hooks are better)
        word_count = len(first_few.split())
        pacing_bonus = 0.10 if (5 <= word_count <= 18) else 0.0
        
        final_score = min(0.15 + score_boost + pacing_bonus, 1.0)
        
        feedback = ""
        if final_score < 0.4:
            feedback = "Hook débil. Intenta añadir misterio, urgencia o una pregunta impactante en los primeros 3 segundos."
        elif final_score < 0.75:
            feedback = "Hook moderado. Puedes aumentar la intriga utilizando palabras de alta tensión como 'imposible' o 'prohibido'."
        else:
            feedback = "Hook excelente. Atrapas al usuario de inmediato con disparadores de alta curiosidad."
            
        return {
            "hook_score": round(final_score, 2),
            "patterns": matched_triggers,
            "has_question": has_question,
            "has_exclamation": has_exclamation,
            "hook_length_words": word_count,
            "feedback": feedback
        }
