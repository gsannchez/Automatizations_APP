import logging
from uuid import UUID
from sqlmodel import select

from ..core.celery_app import celery_app
from ..core.database import get_sync_session
from ..models.generated_video import GeneratedVideo, PipelineState
from ..services.script_generator import ScriptGenerator
from ..services.video_job_service import VideoJobService
from ..schemas.ai_schema import AIScriptRequest
from ..models.template import Template
from ..models.user_settings import UserSettings
from .utils import update_video_status
from .task_helpers import raise_or_retry

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.scripting.scripting_task", bind=True, max_retries=3)
def scripting_task(self, video_id_str: str):
    logger.info(f"▶️ SCRIPTING task started for {video_id_str}")
    video_id = UUID(video_id_str)
    
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            logger.error(f"❌ Video {video_id} not found.")
            return video_id_str

        if video.pipeline_state != PipelineState.QUEUED and video.pipeline_state != PipelineState.SCRIPTING:
            logger.info("⏭️ SCRIPTING ya completado. Omitiendo.")
            return video_id_str

        update_video_status(session, video, PipelineState.SCRIPTING.value, progress=10)

        if video.scenes_data:
            logger.info("⏭️ SCRIPTING scenes ya generadas. Omitiendo.")
            return video_id_str

        job_service = VideoJobService(session)
        job = job_service.create_job(video_id, PipelineState.SCRIPTING.value)

        try:
            # Phase 7.2 Autonomous Learning Core Injection
            topic_to_use = video.topic or "Trending Topic"
            try:
                from ..services.trends_engine.trend_collector import TrendCollector
                from ..services.trends_engine.trend_ranker import TrendRanker
                from ..services.idea_engine.idea_generator import IdeaGenerator
                from ..services.viral_core.hook_optimizer import HookOptimizer
                from ..services.autonomous_learning.performance_feedback import PerformanceFeedbackEngine
                from ..services.autonomous_learning.trend_saturation import TrendSaturationDetector, SaturationState
                from ..services.autonomous_learning.hook_evolution import HookEvolution
                from ..services.autonomous_learning.ab_testing import ABTestingEngine
                from ..services.autonomous_learning.retention_simulator import RetentionSimulator
                from ..services.autonomous_learning.viral_memory import ViralMemorySystem
                from ..services.autonomous_learning.style_recommender import StyleRecommender
                from ..services.autonomous_learning.vector_memory import LightweightVectorMemory
                
                # 1. Collect and rank trends
                collector = TrendCollector(session)
                trends = collector.collect_synthetic_trends()
                top_trends = TrendRanker.get_top(trends, top_n=5)
                
                selected_trend = None
                for t in top_trends:
                    sat = TrendSaturationDetector.detect(t)
                    if sat not in [SaturationState.SATURATED, SaturationState.DEAD]:
                        selected_trend = t
                        break
                
                if not selected_trend and top_trends:
                    selected_trend = top_trends[0] # Fallback if all saturated
                
                if selected_trend:
                    # 2. Idea Generator
                    idea_dict = IdeaGenerator.generate(selected_trend)
                    
                    # 3. Hook Optimizer
                    optimization = HookOptimizer.optimize(idea_dict)
                    
                    # 4. Performance Feedback & Hook Evolution
                    perf_engine = PerformanceFeedbackEngine(session)
                    insights = perf_engine.analyze_history()
                    
                    # 5. A/B Variant Engine
                    ab_variants = ABTestingEngine.generate_variants(idea_dict)
                    idea_dict['hook'] = ab_variants.hook_a # Pick A for primary script
                    
                    # 6. Style Recommender
                    recommended_style = StyleRecommender.recommend(
                        topic=selected_trend.topic, 
                        emotion=idea_dict['emotion'], 
                        platform=video.platform
                    )
                    idea_dict['style'] = recommended_style
                    
                    # 7. Viral Memory
                    memory = ViralMemorySystem(session)
                    memory.persist_hook(idea_dict['hook'], idea_dict['emotion'], optimization['hook_score'])
                    memory.persist_style(recommended_style, video.platform, optimization['hook_score'])

                    # 8. Vector Memory
                    vec_mem = LightweightVectorMemory()
                    vec_mem.add_idea(idea_dict['idea'])
                    
                    # Merge optimized idea with user's topic
                    viral_topic = (
                        f"Target Topic: {topic_to_use}\n"
                        f"Viral Idea: {idea_dict['idea']}\n"
                        f"Optimized Hook: {idea_dict['hook']} (Score: {optimization['hook_score']})\n"
                        f"Style: {idea_dict['style']}, Emotion: {idea_dict['emotion']}\n"
                    )
                    
                    logger.info(f"🧠 Autonomous Learning Core active. Hook score: {optimization['hook_score']}")
                    topic_to_use = viral_topic
                else:
                    logger.warning("No trends found, using base topic.")
                    
            except Exception as e:
                logger.error(f"⚠️ Autonomous Learning Core fallback to manual input. Error: {e}", exc_info=True)

            res_settings = session.execute(select(UserSettings).where(UserSettings.user_id == video.user_id))
            user_settings = res_settings.scalars().first()

            api_key = user_settings.gemini_api_key if user_settings else None
            model_name = user_settings.preferred_gemini_model if user_settings else None

            script_req = AIScriptRequest(
                topic=topic_to_use,
                template_id=video.template_id,
                platform=video.platform,
                api_key=api_key,
                model_name=model_name
            )
            
            template = session.get(Template, video.template_id)
            if not template:
                logger.warning(f"Template {video.template_id} not found. Usando script de fallback y prompt genérico.")
            
            generator = ScriptGenerator()
            script_result = generator.generate(script_req, template)
            if not script_result or not script_result.scenes:
                raise ValueError("AI failed to generate scenes")
            
            scenes = [s.dict() for s in script_result.scenes]
            video.scenes_data = scenes
            
            scene_prog = {}
            for i in range(len(scenes)):
                scene_prog[str(i)] = {"image": "pending", "audio": "pending", "video": "pending"}
            video.scene_progress = scene_prog
            
            session.add(video)
            session.commit()
            job_service.mark_success(job.id)
            logger.info(f"💾 Guardadas {len(scenes)} escenas en base de datos para persistencia.")
            return video_id_str
            
        except Exception as exc:
            job_service.mark_failure(job.id, str(exc))
            update_video_status(session, video, PipelineState.FAILED.value, error_step="SCRIPTING", error_msg=str(exc))
            raise_or_retry(self, exc, countdown=30)

@celery_app.task(name="app.tasks.scripting.validate_task", bind=True)
def validate_task(self, video_id_str: str):
    logger.info(f"▶️ VALIDATE task started for {video_id_str}")
    video_id = UUID(video_id_str)
    with get_sync_session() as session:
        video = session.get(GeneratedVideo, video_id)
        if not video:
            return video_id_str
            
        if video.pipeline_state == PipelineState.SCRIPTING.value or video.pipeline_state == PipelineState.SCRIPTING:
            job_service = VideoJobService(session)
            job = job_service.create_job(video_id, PipelineState.VALIDATED.value)
            # Phase 4: Inject Viral Intelligence Engine scoring
            try:
                from ..services.viral.viral_scorer import ViralScorer
                scorer = ViralScorer(session)
                
                if video.scenes_data:
                    script_text = " ".join([s.get("voiceover_text", "") for s in video.scenes_data if s.get("voiceover_text")])
                    scene_durations = [10.0 for _ in video.scenes_data]  # Default 10s per scene for estimation
                    
                    if script_text:
                        analysis = scorer.analyze_script(script_text, scene_durations, video.id)
                        logger.info(f"🧠 Viral Intelligence scoring completed for video {video.id}. Score: {analysis.overall_score}/100")
                        if analysis.recommendations:
                            for rec in analysis.recommendations:
                                logger.info(f"💡 Viral Suggestion: {rec}")
            except Exception as e:
                logger.error(f"⚠️ Viral scoring injection failed (non-fatal): {e}", exc_info=True)
            
            update_video_status(session, video, PipelineState.VALIDATED.value, progress=15)
            job_service.mark_success(job.id)
        return video_id_str
