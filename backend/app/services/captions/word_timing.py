import re
from typing import List, Dict

class WordTimingEngine:
    """
    Estimates word timestamps using heuristics when a proper ASR model
    (like Whisper) or TTS word-level timings are not available.
    """
    
    @staticmethod
    def estimate_word_timings(text: str, total_duration: float) -> List[Dict]:
        """
        Estimates the start and end time of each word in the text.
        Assumes speaking rate is roughly proportional to character length.
        """
        words = re.findall(r'\S+', text)
        if not words:
            return []
            
        # Remove punctuation for length calculation to be more accurate
        clean_words = [re.sub(r'[^\w\s]', '', w) for w in words]
        total_chars = sum(len(w) for w in clean_words)
        
        # Add a small buffer to avoid division by zero
        if total_chars == 0:
            total_chars = 1
            
        timings = []
        current_time = 0.0
        
        for i, word in enumerate(words):
            clean_word = clean_words[i]
            # Time proportional to word length + a tiny constant for pauses between words
            word_weight = max(1, len(clean_word))
            
            # Simple heuristic: longer words take longer.
            duration = (word_weight / total_chars) * total_duration
            
            # Adjust to not overrun total_duration
            end_time = min(current_time + duration, total_duration)
            
            timings.append({
                "word": word,
                "start": current_time,
                "end": end_time
            })
            
            current_time = end_time
            
        return timings
