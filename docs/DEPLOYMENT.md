# Deployment Guide

Guía de despliegue y desarrollo basada en scripts y configuración del repositorio.

---

## Requisitos previos

| Componente | Versión / nota |
|------------|----------------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | Para Angular |
| Docker Desktop | PostgreSQL + Redis |
| FFmpeg + ffprobe | En PATH |
| NVIDIA + drivers | Para ComfyUI / SDXL local |
| ComfyUI | Puerto 8188, checkpoint en models |
| Ollama | Accesible en `LOCAL_LLM_URL` |
| PowerShell | Scripts Windows |

---

## Desarrollo local (Windows)

### 1. Infraestructura

```powershell
cd c:\Proyectos\Automatizaciones\APP
docker compose up -d
```

Servicios:

- Postgres: `localhost:5432`, user `autovideouser`, pass `autovideopass`, db `autovideodb`
- Redis: `localhost:6379`

### 2. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install slowapi sse-starlette  # usados en código, pueden faltar en requirements
```

Crear `backend/.env` (ejemplo — **no commitear secretos**):

```env
DATABASE_URL=postgresql://autovideouser:autovideopass@localhost:5432/autovideodb
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=
LOCAL_LLM_URL=http://127.0.0.1:11434
COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_STARTUP_ENABLED=true
COMFYUI_START_SCRIPT_PATH=C:\ComfyUI\start_hidden.vbs
JWT_SECRET_KEY=<generar-secreto-fuerte>
ELEVENLABS_API_KEY=
```

Migraciones:

```powershell
alembic upgrade head
```

Arranque API:

```powershell
.\run_backend.ps1
# o: uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`

### 3. Celery (pipeline real)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
$env:PYTHONUTF8=1
celery -A app.core.celery_app worker --pool=solo -Q cpu_queue,gpu_queue,upload_queue -l info
```

Windows **requiere** `--pool=solo`.

Variables útiles:

```env
CELERY_TASK_ALWAYS_EAGER=false
CELERY_MAX_TASKS_PER_CHILD=50
VIDEO_STARTUP_REQUEUE=false
```

### 4. ComfyUI

1. Instalar ComfyUI con checkpoint `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors` en `models/checkpoints/`
2. Ejecutar en `:8188`
3. Verificar: `GET http://127.0.0.1:8188/system_stats`
4. O dejar `COMFYUI_STARTUP_ENABLED` para lanzar VBS en startup API

### 5. Ollama

```bash
ollama pull llama3.1:8b-instruct-q4_K_M
ollama serve
```

Ajustar `LOCAL_LLM_URL` si no es `192.168.1.41`.

### 6. Frontend

```powershell
cd frontend\auto-video-frontend
npm install
npm start
```

Angular: `http://localhost:4200`

### 7. Electron (opcional)

```powershell
npm run electron
```

### Arranque todo-en-uno

```powershell
cd c:\Proyectos\Automatizaciones\APP
.\start_app.ps1
```

Lanza backend, Celery solo cpu_queue implícito en script (`celery ... worker --pool=solo` **sin -Q** — añadir colas manualmente para GPU), frontend y Electron.

**Recomendación:** editar `start_app.ps1` para incluir `-Q cpu_queue,gpu_queue,upload_queue`.

---

## Desarrollo Linux

- Celery puede usar pool `prefork` o `threads`
- Sin `wscript` para ComfyUI — iniciar ComfyUI como systemd user service
- Rutas `COMFYUI_START_SCRIPT_PATH` no aplican
- Mismo docker compose y uvicorn

```bash
celery -A app.core.celery_app worker -Q cpu_queue,gpu_queue,upload_queue -l info --concurrency=2
```

---

## Producción (arquitectura recomendada)

No hay manifests K8s en repo. Patrón sugerido alineado al código:

| Servicio | Réplicas | Notas |
|----------|----------|-------|
| API FastAPI | 2+ | Gunicorn + Uvicorn workers, sin `--reload` |
| Celery CPU | N | composition, scripting, audio |
| Celery GPU | 1 por GPU | solo `gpu_queue` |
| Celery upload | 1 | upload_queue |
| PostgreSQL | 1 HA | Managed |
| Redis | 1 HA | Broker + locks |
| ComfyUI | 1 por GPU | Red interna |
| Object storage | S3 | `STORAGE_TYPE=s3` |
| CDN | Delante de `/media` o signed URLs |

### Variables producción obligatorias

- `JWT_SECRET_KEY` — fuerte, rotación
- `DATABASE_URL` — SSL
- `REDIS_URL` — auth
- `GEMINI_API_KEY`, `ELEVENLABS_API_KEY`
- `ENCRYPTION_KEY` — OAuth tokens
- Desactivar `COMFYUI_STARTUP_ENABLED` en servidor Linux headless si ComfyUI es servicio aparte

### Docker aplicación

No incluido — crear Dockerfile multi-stage:

1. Imagen API: Python slim + ffmpeg
2. Imagen worker-gpu: NVIDIA runtime + ComfyUI client only
3. No empaquetar venv del repo

---

## GPU / NVIDIA

| Uso | VRAM orientativa |
|-----|-----------------|
| ComfyUI SDXL 1024² | 8–12 GB+ |
| SVD / AnimateDiff | 12–24 GB+ |
| SDXL diffusers local | Similar ComfyUI |

`GPUWatchdog` y `ResourcePlanner` leen VRAM; `SAFE_MODE` reduce agresividad orchestrator.

---

## Ollama en producción

- Desplegar Ollama en mismo host GPU o LAN de baja latencia
- Timeout scripting 600 s — considerar modelo más pequeño o Gemini primario

---

## Verificación post-deploy

```bash
curl http://localhost:8000/api/v1/system/pipeline-status
curl http://localhost:8000/api/v1/system/comfyui
```

`celery.available: true` en health.

### Pipeline real manual

```powershell
cd backend
python scripts/run_pipeline_eager.py  # síncrono
# o
python enqueue.py
```

---

## Escalado horizontal

1. Redis como broker central
2. Workers GPU con `worker_prefetch_multiplier=1`
3. Un lock ComfyUI global (`gpu_lock`) — no escalar ComfyUI sin sharding por cola
4. Postgres connection pool en `database.py`

---

## Rollback

- Alembic downgrade
- Redis flush colas solo en mantenimiento (`clear_pipeline_queue.py`)
- Media en S3 versionado
