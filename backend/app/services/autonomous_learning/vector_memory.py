import math
from typing import List

class LightweightVectorMemory:
    """TF-IDF/Cosine Similarity cache to prevent narrative clones."""
    
    def __init__(self):
        self.memory: List[str] = []
        
    def _get_tokens(self, text: str) -> dict:
        tokens = text.lower().split()
        freq = {}
        for t in tokens:
            freq[t] = freq.get(t, 0) + 1
        return freq
        
    def _cosine_sim(self, dict1: dict, dict2: dict) -> float:
        intersection = set(dict1.keys()) & set(dict2.keys())
        numerator = sum([dict1[x] * dict2[x] for x in intersection])
        
        sum1 = sum([dict1[x]**2 for x in dict1.keys()])
        sum2 = sum([dict2[x]**2 for x in dict2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        
        if not denominator:
            return 0.0
        return float(numerator) / denominator

    def check_similarity(self, idea_text: str) -> float:
        """Returns the maximum similarity to existing ideas in memory."""
        if not self.memory:
            return 0.0
            
        new_tokens = self._get_tokens(idea_text)
        max_sim = 0.0
        
        for mem_idea in self.memory:
            mem_tokens = self._get_tokens(mem_idea)
            sim = self._cosine_sim(new_tokens, mem_tokens)
            if sim > max_sim:
                max_sim = sim
                
        return max_sim
        
    def add_idea(self, idea_text: str):
        self.memory.append(idea_text)
