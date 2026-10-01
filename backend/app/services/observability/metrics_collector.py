import logging
import time
from typing import Dict
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

class PrometheusExporter:
    """
    Holds global Prometheus metric definitions to avoid re-registration issues.
    """
    _initialized = False

    if not _initialized:
        # Counters
        TASKS_PROCESSED = Counter('avm_tasks_processed_total', 'Total tasks processed', ['task_type', 'status'])
        
        # Histograms
        TASK_DURATION = Histogram('avm_task_duration_seconds', 'Task duration in seconds', ['task_type'])
        QUEUE_LATENCY = Histogram('avm_queue_latency_seconds', 'Time spent in queue', ['queue_name'])
        
        # Gauges
        ACTIVE_WORKERS = Gauge('avm_active_workers', 'Number of active Celery workers')
        GPU_UTILIZATION = Gauge('avm_gpu_utilization_percent', 'GPU Utilization %', ['node_id'])
        TENANT_QUOTA_USAGE = Gauge('avm_tenant_quota_usage', 'Tenant quota usage %', ['tenant_id'])
        
        # Phase 11.1 Network Metrics
        CHANNEL_COUNT = Gauge('avm_channel_count', 'Total number of managed channels')
        ACTIVE_UNIVERSES = Gauge('avm_active_universes', 'Number of active narrative universes')
        AVERAGE_GROWTH_SCORE = Gauge('avm_average_growth_score', 'Average growth score across network')
        PUBLISHING_QUEUE_LOAD = Gauge('avm_publishing_queue_load', 'Number of videos waiting to be published')
        SATURATION_ALERTS = Counter('avm_saturation_alerts', 'Number of niche saturation alerts triggered')

        # Phase 11.2 Metrics
        CHANNEL_SIMILARITY_SCORE = Gauge('avm_channel_similarity_score', 'Average channel similarity')
        PATTERN_PROPAGATION_RATE = Gauge('avm_pattern_propagation_rate', 'Rate of pattern propagation')
        CONTAMINATION_BLOCKS = Counter('avm_contamination_blocks', 'Count of contamination blocks')
        DIVERSITY_INDEX_GLOBAL = Gauge('avm_diversity_index_global', 'Global diversity index')

        # Phase 11.3 Metrics
        UNIVERSE_ARC_COMPLETION_RATE = Gauge('avm_universe_arc_completion_rate', 'Rate of completed arcs')
        CHARACTER_CONSISTENCY_SCORE = Gauge('avm_character_consistency_score', 'Character emotional stability score')
        LORE_CONFLICT_COUNT = Counter('avm_lore_conflict_count', 'Number of lore contradictions detected')
        CROSSOVER_SUCCESS_RATE = Gauge('avm_crossover_success_rate', 'Rate of successful soft crossovers')
        UNIVERSE_GROWTH_VELOCITY = Gauge('avm_universe_growth_velocity', 'Speed of universe expansion')

        # Phase 11.4 Metrics
        CONTENT_VALUE_SCORE = Gauge('avm_content_value_score', 'Content value score')
        CHANNEL_ROI_ESTIMATE = Gauge('avm_channel_roi_estimate', 'Channel ROI estimate')
        GPU_EFFICIENCY = Gauge('avm_gpu_efficiency', 'GPU allocation efficiency')
        WASTE_RATIO = Gauge('avm_waste_ratio', 'Content waste ratio')
        # Phase ElevenLabs Metrics
        TTS_GENERATION_TIME = Histogram('avm_tts_generation_time_seconds', 'Time spent generating TTS', ['voice_id'])
        TTS_CACHE_HIT_RATE = Counter('avm_tts_cache_hits', 'Number of TTS cache hits')
        TTS_FAILURES = Counter('avm_tts_failures', 'Number of TTS generation failures')
        # Phase Scene Timeline Metrics
        SCENE_DURATION_DISTRIBUTION = Histogram('avm_scene_duration_distribution', 'Distribution of scene durations in seconds')
        AUDIO_GENERATION_LATENCY = Histogram('avm_audio_generation_latency', 'Latency of full audio generation cycle')
        TIMELINE_SYNC_ACCURACY = Gauge('avm_timeline_sync_accuracy', 'Measures sync drift between audio and video frames')
        SCENE_PIPELINE_COMPLETION_RATE = Counter('avm_scene_pipeline_completion_rate', 'Rate of completed scenes')
        
        _initialized = True

class MetricsCollector:
    """
    Helper class to record metrics during task execution.
    Should be injected or instantiated at the task level.
    """
    def __init__(self, task_type: str):
        self.task_type = task_type
        self.start_time = None

    def start_timer(self):
        self.start_time = time.time()

    def record_success(self):
        PrometheusExporter.TASKS_PROCESSED.labels(task_type=self.task_type, status='success').inc()
        if self.start_time:
            duration = time.time() - self.start_time
            PrometheusExporter.TASK_DURATION.labels(task_type=self.task_type).observe(duration)

    def record_failure(self):
        PrometheusExporter.TASKS_PROCESSED.labels(task_type=self.task_type, status='failure').inc()

    @staticmethod
    def record_queue_latency(queue_name: str, latency_seconds: float):
        PrometheusExporter.QUEUE_LATENCY.labels(queue_name=queue_name).observe(latency_seconds)

    @staticmethod
    def update_gpu_utilization(node_id: str, utilization: float):
        PrometheusExporter.GPU_UTILIZATION.labels(node_id=node_id).set(utilization)
