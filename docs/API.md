# API Documentation

Base URL desarrollo: `http://localhost:8000`  
OpenAPI automático: `http://localhost:8000/docs`  
Versión declarada en `FastAPI`: **8.0.0**

## Autenticación

La mayoría de endpoints de vídeos y settings requieren header:

```http
Authorization: Bearer <access_token>
```

Obtenido vía `POST /api/v1/auth/login`. Los endpoints de `auth/register`, `auth/login`, raíz `/`, y varios módulos virales usan sesión sync o sin auth según implementación — ver cada sección.

CORS permitido: `http://localhost:4200`, `4000`, `127.0.0.1:4200`, `4000`.

Rate limiting: `slowapi` en `app.state.limiter` (deshabilitado si `TESTING=1`).

---

## Endpoints raíz (`main.py`)

### `GET /`

**Respuesta 200:**

```json
{
  "status": "backend ok",
  "version": "4.0.0",
  "phase": "Viral Intelligence Engine"
}
```

Nota: discrepancia con `FastAPI(version="8.0.0")`.

### `GET /api/v1/ai-backends`

Lista backends de vídeo IA futuros (`VideoGeneratorFactory`).

---

## Auth — prefijo `/api/v1/auth`

### `POST /register`

| Campo body | Tipo | Obligatorio |
|------------|------|-------------|
| email | string | sí |
| password | string | sí |

**Respuesta 200:** `UserRead`  
**Errores:** 400 si email existe

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

### `POST /login`

Body: `UserLogin` (`email`, `password`)

**Respuesta 200:**

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

**Errores:** 401 credenciales incorrectas

### `GET /me`

Requiere JWT. **Respuesta:** `UserRead`

### `GET /stats`

Requiere JWT. Cuenta vídeos, plantillas, canales del usuario.

---

## Videos — prefijo `/api/v1/videos`

Todos requieren JWT salvo que se indique lo contrario.

### `GET /`

Query: `page` (default 1), `limit` (1–100, default 20)

**Respuesta:** `GeneratedVideoPage` `{ items, total, page, limit }`

### `POST /`

Body `GeneratedVideoCreate`:

```json
{
  "template_id": "uuid",
  "title": "Mi vídeo",
  "platform": "TIKTOK",
  "topic": "Tema opcional",
  "channel_id": null,
  "style_config": null
}
```

Crea registro `status=QUEUED`, `pipeline_state=QUEUED`.

### `GET /{video_id}`

**404** si no existe o no es del usuario (soft-delete excluido).

### `GET /{video_id}/status`

Contrato de polling frontend (~2 s). Schema `GeneratedVideoStatus`: `id`, `status`, `pipeline_state`, `progress`, `error_message`.

### `GET /{video_id}/download`

**409** si `status != DONE`  
**200:**

```json
{
  "download_url": "/media/<ruta-publica>",
  "filename": "<nombre-descarga>.mp4"
}
```

El `storage_key` interno no se expone; este endpoint es el contrato estable de acceso al archivo cuando `status` es `DONE`.

### `PATCH /{video_id}`

Body `GeneratedVideoUpdate`: `status`, `storage_key` opcionales.

### `DELETE /{video_id}`

Soft delete: `is_deleted=true`, `deleted_at` UTC.

### `POST /{video_id}/generate`

Query opcional: `music_file` (string; reservado para música de fondo en composición).

**Flujo interno:** resetea estado del vídeo → encola `process_video_workflow.delay(video_id)` en Celery.

**Respuesta 200:**

```json
{
  "message": "Video generation started",
  "video_id": "uuid",
  "music_file": null
}
```

### `POST /{video_id}/retry`

Igual que generate si no está `DONE`. **409** si ya completado.

---

## AI — prefijo `/api/v1/ai`

### `POST /generate-script`

Body `AIScriptRequest`:

| Campo | Tipo | Default |
|-------|------|---------|
| topic | string | — |
| template_id | UUID/int | — |
| tone | string | Professional |
| target_audience | string | General |
| language | string | Spanish |
| platform | string | YouTube |

**Servicios:** `ScriptGenerator`, template DB sync session.

**Respuesta:** `{ "scenes": [ { "text", "duration", "image_prompt" } ] }`  
**Errores:** 404 template, 500 generación

### `POST /enhance-text`

Body: `{ "title", "topic" }` → LLM Ollama JSON → `{ "title", "topic" }` mejorados.

---

## Templates — `/api/v1/templates`

CRUD sync session: `GET /`, `POST /`, `GET /{id}`, `DELETE /{id}`.

---

## Channels — `/api/v1/channels`

`GET /`, `POST /`, `GET /{channel_id}` (int), `DELETE /{channel_id}`.

---

## Settings — `/api/v1/settings`

JWT requerido. `GET /` y `PATCH /` para `UserSettings` (API keys Gemini, modelos, `extra_config` JSONB).

---

## System — prefijo `/api/v1/system`

Router interno con `prefix="/system"` → rutas:

| Método | Ruta completa | Descripción |
|--------|---------------|-------------|
| GET | `/api/v1/system/health` | Pipeline + Celery heartbeat |
| GET | `/api/v1/system/gpu` | VRAM vía GPUWatchdog |
| GET | `/api/v1/system/comfyui` | Estado ComfyUI |
| GET | `/api/v1/system/pipeline-status` | Agregado health+gpu+comfyui |

---

## Trends — `/api/v1/trends`

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Lista trending topics |
| GET | `/{topic_id}` | Detalle |
| POST | `/refresh` | Recolecta/actualiza trends |
| DELETE | `/{topic_id}` | Borra topic |

---

## Viral score — `/api/v1/viral-score`

Montado con prefix `viral-score` en main (router viral).

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/score` | Analiza script/contenido |
| GET | `/history` | Historial análisis |
| GET | `/{analysis_id}` | Análisis por ID |

---

## Clips — `/api/v1/clips`

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/analyze` | Job análisis de clip |
| GET | `/` | Lista análisis |
| GET | `/{clip_id}` | Detalle |
| DELETE | `/{clip_id}` | Borrar registro |

---

## Analytics — `/api/v1/analytics`

| Método | Ruta |
|--------|------|
| POST | `/metrics` |
| GET | `/metrics/{video_id}` |
| POST | `/retention-analysis` |
| POST | `/predict` |
| POST | `/recommendations` |
| GET | `/recommendations` |

---

## Styles — `/api/v1/styles`

| Método | Ruta |
|--------|------|
| GET | `/` |
| GET | `/{style_id}` |
| POST | `/apply` |
| GET | `/ids/list` |

---

## Learning — `/api/v1/learning`

| Método | Ruta |
|--------|------|
| GET | `/insights` |
| GET | `/saturation` |
| GET | `/top-hooks` |
| GET | `/platform-stats` |

---

## Orchestration — `/api/v1/orchestration`

| Método | Ruta | Servicio |
|--------|------|----------|
| GET | `/status` | MasterOrchestrator |
| GET | `/agents` | Lista agentes |
| GET | `/queue-health` | ContentScheduler pending |
| GET | `/system-load` | ResourcePlanner |
| GET | `/decisions` | Decision engine |
| GET | `/campaigns` | CampaignManager |
| POST | `/campaigns?name=&total_episodes=` | Crear campaña |
| POST | `/recover` | Recovery sweep |
| POST | `/feedback-cycle` | AnalyticsFeedback |
| GET | `/schedule` | Content schedule |
| GET | `/event-stream` | SSE (requiere `sse-starlette`) |

---

## Routers NO montados en `main.py`

Disponibles en código pero **inaccesibles** hasta `include_router`:

### Director — router prefix `/director`

Rutas: `/status/{job_id}`, `/quality/{job_id}`, `/narrative/{job_id}`, `/variants/{job_id}`, `/regeneration/{job_id}`, `/consistency/{job_id}`.

Si se montara: `app.include_router(director_router, prefix="/api/v1/director")`.

### Economy — prefix `/economy`

`/gpi`, `/value-map`, `/rebalance`, `/waste-report`, `/allocation`.

### Images — prefix `/images`

`POST /generate`, `GET /health`, `POST /warmup` — SDXL/Comfy directo.

### Network — prefix `/network`

Canales de red narrativa, universos, patrones, crossover — ver `network.py`.

---

## Códigos de error comunes

| Código | Contexto |
|--------|----------|
| 401 | JWT inválido o ausente |
| 404 | Recurso no encontrado o no owned |
| 409 | Download antes de DONE / retry en DONE |
| 429 | Rate limit exceeded (slowapi) |
| 500 | Fallo LLM, DB, pipeline |

---

## Ejemplo flujo completo (curl)

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}' | jq -r .access_token)

# Crear vídeo
VID=$(curl -s -X POST http://localhost:8000/api/v1/videos/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"template_id":"<uuid>","title":"Test","platform":"TIKTOK","topic":"AI tools"}' | jq -r .id)

# Generar (encola Celery)
curl -X POST "http://localhost:8000/api/v1/videos/$VID/generate" \
  -H "Authorization: Bearer $TOKEN"

# Poll (requiere worker Celery en ejecución)
curl -s "http://localhost:8000/api/v1/videos/$VID/status" \
  -H "Authorization: Bearer $TOKEN"
```
