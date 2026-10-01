# Services Documentation

Catálogo de servicios en `backend/app/services/`. Cada entrada: responsabilidad, I/O, dependencias clave.

---

## Servicios del pipeline core

### ScriptGenerator (`script_generator.py`)

| | |
|--|--|
| **Responsabilidad** | Guiones JSON por escena vía LLM |
| **Inputs** | `AIScriptRequest`, `Template` opcional |
| **Outputs** | `AIScriptResponse` |
| **Dependencias** | `llm_client`, `gemini_client` |
| **Público** | `generate()`, `_build_system_prompt()`, `_generate_fallback_script()` |
| **Riesgos** | Timeout 600s bloquea worker |
| **Mejoras** | Streaming JSON validation |

### ImageGenerator / `generate_images_for_scenes` (`image_generator.py`)

| | |
|--|--|
| **Responsabilidad** | Wrapper sync ComfyUI por escenas |
| **Inputs** | lista scene dicts, timeout |
| **Outputs** | paths storage |
| **Dependencias** | `ComfyUIGenerator`, `TemporalConsistencyEngine`, `storage` |
| **Riesgos** | Event loop anidado |

### VideoGenerator (`video_generator.py`)

| | |
|--|--|
| **Responsabilidad** | Ensamblado FFmpeg, Ken Burns, calidad |
| **Inputs** | scenes[], output filename |
| **Outputs** | storage_key final |
| **Dependencias** | storage, HybridGenerator, SceneQualityAnalyzer, AdaptiveEditor, tts_service |
| **Métodos clave** | `assemble_video`, `_create_scene_clip`, `_get_audio_duration` |

### video_recovery (`video_recovery.py`)

| | |
|--|--|
| **Responsabilidad** | Requeue Celery al startup |
| **Config** | VIDEO_STARTUP_* env |

### video_job_service (`video_job_service.py`)

| | |
|--|--|
| **Responsabilidad** | CRUD jobs por paso pipeline |
| **Métodos** | `create_job`, `mark_success`, `mark_failure` |

### comfyui_health (`comfyui_health.py`)

| | |
|--|--|
| **Responsabilidad** | Ping ComfyUI, diagnóstico URL |

---

## AI / Imagen

### ComfyUIGenerator (`ai/image_generation/comfyui_generator.py`)

Ver [AI_PIPELINE.md](./AI_PIPELINE.md).

### SDXLGenerator (`ai/image_generation/sdxl_generator.py`)

Diffusers local alternativo a ComfyUI.

### ImageCache, prompt_enhancer, model_manager, gpu_image_guard, image_quality

Caché, mejora prompts, warmup GPU, guardas VRAM.

### BaseImageGenerator (`ai/base/base_image_generator.py`)

Interfaz abstracta para generadores.

---

## TTS

### ElevenLabsTTS (`tts/elevenlabs_tts.py`)

Shim async — reemplazar por SDK.

### VoiceRegistry (`tts/voice_registry.py`)

Mapeo character → voice_id.

### fallback_tts, audio_cache

Cadena fallback y caché.

### tts_service (`tts_service.py`)

gTTS sync para assemble cuando falta audio_path.

---

## Timeline

### SceneTimelineEngine (`timeline/scene_timeline_engine.py`)

`build_canonical_scene`, `merge_media_state`, `validate_timeline`.

---

## Video AI

| Servicio | Rol |
|----------|-----|
| hybrid_generator | Motion por escena |
| svd_generator | SVD |
| animatediff_generator | AnimateDiff |
| temporal_consistency | Seeds y FreeU |
| video_generator_factory | Selección backend |
| video_generator_future | Kling, Runway, Veo |

---

## Director / Calidad

| Servicio | Rol |
|----------|-----|
| creative_decision_engine | Mutación prompts regeneración |
| scene_supervisor | Validación guion pre-render |
| scene_quality_analyzer | Métricas flicker etc. |

### adaptive_editor, editing_modules

Timeline emocional y transiciones.

### visual_fx/transitions, consistency/scene_transition_manager

Efectos entre escenas.

---

## Viral y aprendizaje

| Módulo | Rol |
|--------|-----|
| trends_engine/trend_collector | Trends sintéticos/DB |
| trends_engine/trend_ranker | Top N |
| idea_engine/idea_generator | Ideas desde trend |
| viral_core/hook_optimizer | Score hooks |
| autonomous_learning/* | Feedback, A/B, saturación, memoria |
| viral/* | Scoring API |

---

## Orquestación (Phase 8)

| Servicio | Rol |
|----------|-----|
| master_orchestrator | Estado agentes, recovery |
| campaign_manager | Campañas episodicas |
| content_scheduler | Cola publicación |
| resource_planner | VRAM/RAM/disk thresholds |
| analytics_feedback | Ciclo feedback estilos |
| event_bus | SSE eventos |
| scene_orchestrator | Orquestación escenas |

---

## Storage

| Servicio | Rol |
|----------|-----|
| storage/local.py | Filesystem bajo backend |
| storage/s3.py | boto3 |
| storage/key_builder.py | Rutas canónicas videos/{id}/final.mp4 |
| storage/__init__.py | Factory STORAGE_TYPE |

---

## Health / Observability

| Servicio | Rol |
|----------|-----|
| health/pipeline_health | Celery heartbeat Redis |
| health/celery_health | Inspect alternativo |
| monitoring/gpu_watchdog | VRAM |
| observability/metrics_collector | Métricas |

---

## Economía / Red (API no montada)

| Servicio | Rol |
|----------|-----|
| economy/global_performance_index | GPI |
| economy/resource_allocator | Asignación recursos |
| channel_network/* | Diversidad, patrones |
| universe_engine/* | Lore, arcos, personajes |

---

## Render

`render/render_pipeline.py` y módulos relacionados — pipeline render alternativo/extensión.

---

## Integraciones externas

| Servicio | Rol |
|----------|-----|
| youtube_service | Upload OAuth |
| social_media_service | Redes |
| automatic1111_client | A1111 legacy |

---

## Patrón de uso típico (Celery)

```
scripting_task → ScriptGenerator + viral modules
generate_image_task → image_generator → ComfyUIGenerator
generate_audio_task → ElevenLabsTTS + VoiceRegistry
compose_video_task → VideoGenerator.assemble_video
```

---

## Servicios stub / placeholder

| Servicio | Nota |
|----------|------|
| director_tasks (tasks) | Log only |
| encode_video_task | No transcode real |
| upload_task | Marca DONE sin upload |
| ElevenLabsTTS | Path fake |

Mejora global: interfaz `PipelineBackend` unificada para orquestar pasos Celery y extensiones futuras.
