# Security Analysis

Análisis de seguridad basado en revisión estática del código de aplicación (excl. venv).

---

## Resumen ejecutivo

| Clasificación | Cantidad aprox. |
|---------------|-----------------|
| Crítica | 1 |
| Alta | 4 |
| Media | 6 |
| Baja | 5 |

---

## Hallazgos

### CRÍTICA-1: JWT secret por defecto inseguro

**Ubicación:** `core/config.py`

```python
JWT_SECRET_KEY: str = "change-me-in-production"
```

**Riesgo:** Forge de tokens si no se sobreescribe en `.env`.  
**Mitigación:** Obligar secreto ≥256 bits en producción; fallar startup si valor default.

---

### ALTA-1: Credenciales por defecto en docker-compose

**Ubicación:** `docker-compose.yml`

```yaml
POSTGRES_PASSWORD: autovideopass
```

**Riesgo:** Exposición si puerto 5432 publicado en red no confiable.  
**Mitigación:** Secrets Docker, no publicar puertos en prod, contraseñas fuertes.

---

### ALTA-2: API keys en UserSettings sin cifrado documentado en lectura API

**Ubicación:** `models/user_settings.py`, `settings.py` API

**Riesgo:** `gemini_api_key` en DB; si endpoint settings filtra campos sensibles incorrectamente → leak.  
**Mitigación:** Cifrar en reposo con `ENCRYPTION_KEY`; nunca devolver keys completas en GET (solo máscara).

---

### ALTA-3: CORS amplio en desarrollo

**Ubicación:** `main.py` — localhost:4200/4000

**Riesgo:** Bajo en dev; en prod si se copia igual + credentials true → CSRF-like desde origen malicioso.  
**Mitigación:** Lista blanca por entorno `ALLOWED_ORIGINS`.

---

### ALTA-4: Endpoints sin autenticación

| Endpoint | Riesgo |
|----------|--------|
| `POST /api/v1/ai/generate-script` | Abuso LLM, coste Gemini |
| Templates/Channels CRUD sync | Sin JWT en código auditado |
| Orchestration SSE | Sin auth |
| System health | Info disclosure infra |

**Mitigación:** `Depends(get_current_user)` uniforme; API keys para servicios internos.

---

### MEDIA-1: ComfyUI sin autenticación asumida

**Riesgo:** Cualquier host en red puede encolar prompts en :8188.  
**Mitigación:** Firewall, reverse proxy con auth, solo localhost.

---

### MEDIA-2: Redis sin password en compose

**Riesgo:** Acceso cola/broker en LAN.  
**Mitigación:** `requirepass`, TLS, red Docker interna.

---

### MEDIA-3: Rate limiting parcial

`slowapi` configurado globalmente; no por usuario/plan.  
**Mitigación:** Límites por `user_id` y endpoint `/generate`.

---

### MEDIA-4: Soft delete no borra media

Vídeos borrados mantienen archivos en storage.  
**Mitigación:** Job de purga GDPR.

---

### MEDIA-5: Logs pueden contener prompts y PII

Scripting loguea topics y respuestas LLM parciales.  
**Mitigación:** Redactar en producción.

---

### MEDIA-6: Dependencias no pinneadas (torch, boto3)

Supply chain drift.  
**Mitigación:** Lock file, escaneo CVE.

---

### BAJA-1: `sse-starlette` / `slowapi` ausentes de requirements.txt

DoS por import error en deploy limpio — operacional.

---

### BAJA-2: Versión API inconsistente en `/` vs OpenAPI

Informational.

---

### BAJA-3: Electron carga localhost — MITM en red local

Cert pinning si carga remota en futuro.

---

### BAJA-4: Test user hardcoded en `run_pipeline_test.py`

Solo dev scripts.

---

### BAJA-5: OAuth YouTube secrets en env sin rotación documentada

`YOUTUBE_CLIENT_ID/SECRET`.

---

## Secrets — dónde se leen

| Secret | Fuente |
|--------|--------|
| JWT_SECRET_KEY | config / .env |
| GEMINI_API_KEY | env, UserSettings |
| ELEVENLABS_API_KEY | env |
| AWS_* | env S3 |
| ENCRYPTION_KEY | env |
| KLING/RUNWAY | env video futuro |

**No se encontraron API keys hardcodeadas en `backend/app/`** (grep patrones literales en app).

---

## Endpoints sensibles

| Ruta | Datos |
|------|-------|
| GET /videos/{id}/download | URL media |
| PATCH /settings | API keys usuario |
| POST /auth/login | Credenciales |

Usar siempre HTTPS en producción.

---

## Checklist hardening pre-auditoría

- [ ] Rotar `JWT_SECRET_KEY` y `POSTGRES_PASSWORD`
- [ ] Auth en todos los routers de mutación
- [ ] ComfyUI solo red privada
- [ ] Redis AUTH
- [ ] CORS producción restrictivo
- [ ] Escaneo `pip audit` / `npm audit`
- [ ] `.env` en `.gitignore` verificado
