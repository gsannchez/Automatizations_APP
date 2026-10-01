from sqlmodel import Session
from ...models.viral_intelligence import ViralPattern, HookTemplate, StylePerformance

class ViralMemorySystem:
    """Persists successful patterns into the database."""
    
    def __init__(self, session: Session):
        self.session = session
        
    def persist_hook(self, hook_text: str, emotion: str, score: float):
        template = HookTemplate(
            template_text=hook_text,
            emotion=emotion,
            score=score,
            usage_count=1,
            success_rate=0.5
        )
        self.session.add(template)
        self.session.commit()
        
    def persist_style(self, style_name: str, platform: str, score: float):
        perf = StylePerformance(
            style_name=style_name,
            platform=platform,
            score=score,
            usage_count=1,
            success_rate=0.5
        )
        self.session.add(perf)
        self.session.commit()
