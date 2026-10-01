"""
app/services/variants/battle_engine.py

Phase 10: Coordinates the generation, scoring, and selection of script variants.
Saves battle results to the database.
"""
import logging
from typing import Dict, Any

from .variants_modules import VariantGenerator, VariantScorer, WinnerSelector
from app.models.director import VariantBattle
from sqlmodel import Session

logger = logging.getLogger(__name__)

class BattleEngine:
    def __init__(self, session: Session):
        self.session = session
        self.generator = VariantGenerator()
        self.scorer = VariantScorer()
        self.selector = WinnerSelector()

    def run_hook_battle(self, base_script: Dict[str, Any], job_id: str, tenant_id: str) -> Dict[str, Any]:
        """
        Generates hook variants, scores them, picks a winner, and records the battle.
        """
        logger.info(f"[BattleEngine] Starting hook battle for job {job_id}")
        
        # 1. Generate
        variants = self.generator.generate_hook_variants(base_script, count=3)
        
        # 2. Score
        scored_variants = []
        for i, var in enumerate(variants):
            score = self.scorer.score_hook(var)
            scored_variants.append({
                "variant_id": f"var_{i}",
                "script": var,
                "score": score
            })
            
        # 3. Select Winner
        winner = self.selector.select_best(scored_variants)
        
        # 4. Persist
        battle = VariantBattle(
            tenant_id=tenant_id,
            job_id=job_id,
            battle_type="hook",
            variants={v["variant_id"]: v["score"] for v in scored_variants},
            winner_id=winner["variant_id"]
        )
        self.session.add(battle)
        self.session.commit()
        
        logger.info(f"[BattleEngine] Winner selected: {winner['variant_id']} with score {winner['score']:.2f}")
        
        return winner["script"]
