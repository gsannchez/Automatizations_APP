# Flujo de Prueba Completa del Sistema

## 🚀 Inicio Rápido

### Opción 1: Script Automatizado

```powershell
cd c:\Proyectos\Automatizaciones\APP\backend
.\test_system.ps1
```

### Opción 2: Prueba Rápida (sin instalación completa)

```powershell
.\test_system.ps1 -SkipInstall -QuickTest
```

### Opción 3: Sin Redis

```powershell
.\test_system.ps1 -SkipRedis
```

---

## 📋 Flujo Manual Completo

### 1. Preparación del Entorno

#### 1.1 Activar Entorno Virtual

```powershell
cd c:\Proyectos\Automatizaciones\APP\backend
.\venv\Scripts\Activate.ps1
```

#### 1.2 Instalar/Actualizar Dependencias

```powershell
pip install -r requirements.txt
```

#### 1.3 Configurar .env

Asegúrate de tener:

```env
GEMINI_API_KEY=tu_api_key_real
ENCRYPTION_KEY=clave_generada_con_fernet
REDIS_URL=redis://localhost:6379/0
```

---

### 2. Iniciar Servicios

#### 2.1 Redis (Terminal 1)

```powershell
# Con Docker
docker run -d -p 6379:6379 redis:alpine

# O instalación local
redis-server
```

#### 2.2 AUTOMATIC1111 (Terminal 2) - Opcional

```powershell
# Si tienes Stable Diffusion instalado
cd path\to\stable-diffusion-webui
.\webui.bat --api
```

#### 2.3 Celery Worker (Terminal 3)

```powershell
cd c:\Proyectos\Automatizaciones\APP\backend
.\venv\Scripts\Activate.ps1
celery -A app.core.celery_app worker --pool=solo -l info
```

#### 2.4 Servidor FastAPI (Terminal 4)

```powershell
cd c:\Proyectos\Automatizaciones\APP\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

---

### 3. Verificación de Servicios

#### 3.1 Verificar FastAPI

Abrir navegador en: http://localhost:8000/docs

Deberías ver la interfaz Swagger UI.

#### 3.2 Verificar Redis

```powershell
python -c "import redis; r=redis.Redis(); print(r.ping())"
# Output esperado: True
```

#### 3.3 Verificar Celery

En la terminal de Celery deberías ver:

```
[tasks]
  . app.tasks.generate_video_task

celery@HOSTNAME ready.
```

---

### 4. Ejecutar Pruebas Automatizadas

#### 4.1 Pruebas Unitarias

```powershell
python -m pytest app/tests/test_script_generator.py -v
python -m pytest app/tests/test_image_generation.py -v
python -m pytest app/tests/test_video_assembly.py -v
```

#### 4.2 Pruebas de Integración

```powershell
python -m pytest app/tests/test_integration.py -v
python -m pytest app/tests/test_automation.py -v
```

#### 4.3 Pruebas Completas

```powershell
python -m pytest app/tests/ -v --tb=short
```

---

### 5. Pruebas de API (vía Swagger)

#### 5.1 Acceder a Swagger UI

http://localhost:8000/docs

#### 5.2 Crear Plantilla (Template)

1. Expandir `POST /api/v1/templates/`
2. Click "Try it out"
3. Body:

```json
{
  "name": "Template de Prueba",
  "description": "Para testing completo",
  "structure_json": "[{\"duration\": 5}, {\"duration\": 5}, {\"duration\": 5}]"
}
```

4. Execute
5. Copiar `id` del response

#### 5.3 Generar Guion con IA

1. Expandir `POST /api/v1/ai/generate-script`
2. Body:

```json
{
  "topic": "Inteligencia Artificial en 2025",
  "template_id": 1,
  "tone": "Professional",
  "target_audience": "General",
  "language": "Spanish",
  "platform": "YouTube"
}
```

3. Execute
4. Verificar que devuelve un array de escenas con:
   - `text`: Narración
   - `duration`: Segundos
   - `image_prompt`: Prompt para SD

#### 5.4 Crear Solicitud de Video

1. Expandir `POST /api/v1/videos/`
2. Body:

```json
{
  "topic": "Test Sistema Completo",
  "template_id": 1,
  "status": "pending"
}
```

3. Execute
4. Copiar `id` del video

#### 5.5 Encolar Generación

1. Expandir `POST /api/v1/videos/{video_id}/generate`
2. Ingresar el ID del video
3. Execute
4. Verificar response:

```json
{
  "message": "Video generation queued via Celery",
  "video_id": 1
}
```

#### 5.6 Monitorear Estado

1. En la terminal de Celery verás:

```
[INFO] Task app.tasks.generate_video_task[...] received
[INFO] 🚀 Starting background video generation for ID: 1
```

2. Para ver el estado del video:
   - `GET /api/v1/videos/{video_id}`
   - Campo `status`: "queued" → "processing" → "success"

---

### 6. Pruebas de Componentes Individuales

#### 6.1 Prueba de Encriptación

```powershell
python -c @"
from app.core.encryption import encrypt_token, decrypt_token
original = 'test_oauth_token_123'
encrypted = encrypt_token(original)
decrypted = decrypt_token(encrypted)
print(f'Original: {original}')
print(f'Encrypted: {encrypted}')
print(f'Decrypted: {decrypted}')
print(f'Match: {original == decrypted}')
"@
```

#### 6.2 Prueba de Generador de Guiones (Script Generator)

```powershell
python -c @"
from app.services.script_generator import ScriptGenerator
from app.schemas.ai_schema import AIScriptRequest
from app.models.template import Template

generator = ScriptGenerator()
request = AIScriptRequest(
    topic='Tecnología 2025',
    template_id=1,
    tone='Casual',
    platform='TikTok'
)
template = Template(id=1, name='T', structure_json='[]')

# Esto hará llamada real a Gemini
# result = generator.generate(request, template)
# print(f'Scenes: {len(result.scenes)}')
print('Generator ready for testing')
"@
```

#### 6.3 Prueba de TTS (Texto a Voz)

```powershell
python -c @"
from app.services.tts_service import tts_service
import os

text = 'Esta es una prueba del sistema de texto a voz'
audio_path = tts_service.generate_audio(text, 'test_tts.mp3')
print(f'Audio generado en: {audio_path}')
print(f'Archivo existe: {os.path.exists(audio_path)}')
"@
```

#### 6.4 Prueba de Caché

```powershell
python -c @"
import asyncio
from app.core.cache import cache

async def test_cache():
    await cache.set('test_key', {'data': 'test_value'}, expire=60)
    value = await cache.get('test_key')
    print(f'Cached value: {value}')
    await cache.delete('test_key')

asyncio.run(test_cache())
"@
```

---

### 7. Generación de Video Completa (End-to-End)

#### Prerequisitos

- ✅ Gemini API Key configurada
- ✅ AUTOMATIC1111 corriendo (opcional, puede fallar con elegancia/gracefully)
- ✅ Worker de Celery activo
- ✅ Redis corriendo

#### Proceso

1. **Crear Plantilla** (si no existe)
2. **Crear Petición de Video** via API
3. **Encolar Generación** con `POST /videos/{id}/generate`
4. **Monitorear Worker de Celery**:

```
🚀 Starting background video generation for ID: 1
🎨 Generating image for scene 0...
🎨 Generating image for scene 1...
🎬 Rendering scene 0...
🎬 Rendering scene 1...
🔗 Concatenating scenes...
✅ Video generated: C:\...\videos\video_..._....mp4
✅ Video generation completed for ID: 1
```

5. **Verificar Video**:
   - Ir a `c:\Proyectos\Automatizaciones\APP\videos\`
   - Buscar el archivo `.mp4` generado
   - Reproducir para verificar

---

### 8. Verificación de Registros (Logs)

#### 8.1 Logs de la Aplicación

```powershell
Get-Content app.log -Tail 50
```

Deberías ver logs en formato JSON:

```json
{
  "timestamp": "2025-11-23T18:00:00",
  "level": "INFO",
  "message": "Video generation started"
}
```

#### 8.2 Logs de Celery

Ver la terminal donde corre Celery para:

- Tareas recibidas
- Progreso de generación
- Errores si los hay

#### 8.3 Logs de FastAPI

Ver la terminal de uvicorn para:

- Peticiones HTTP
- Errores de API
- Advertencias (Warnings)

---

### 9. Limpieza (opcional)

#### 9.1 Detener Servicios

```powershell
# FastAPI: Ctrl+C en su terminal
# Celery: Ctrl+C en su terminal
# Redis: docker stop <container_id>
```

#### 9.2 Limpiar Archivos Temporales

```powershell
Remove-Item -Recurse -Force generated_images\*
Remove-Item -Recurse -Force generated_audio\*
Remove-Item -Recurse -Force videos\tmp_*
```

#### 9.3 Limpiar Base de Datos (cuidado)

```powershell
Remove-Item database.db
# Después recrear con init_db()
```

---

## 🎯 Lista de Verificación (Checklist)

### Configuración Inicial

- [ ] Python 3.11+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas
- [ ] Archivo `.env` configurado
- [ ] GEMINI_API_KEY válida

### Servicios

- [ ] Redis corriendo en puerto 6379
- [ ] Worker de Celery activo
- [ ] FastAPI respondiendo en puerto 8000
- [ ] AUTOMATIC1111 (opcional) en puerto 7861

### Pruebas

- [ ] Pruebas unitarias pasando
- [ ] Pruebas de integración pasando
- [ ] Endpoints de la API respondiendo

### Funcionalidad

- [ ] Generación de guion con Gemini funciona
- [ ] Generación de imágenes (o fallback) funciona
- [ ] TTS genera audio correctamente
- [ ] Ensamblaje de video se completa sin errores
- [ ] Celery procesa tareas correctamente

### Avanzado

- [ ] Encriptación de tokens funciona
- [ ] Caché de Redis operativo
- [ ] Programador de tareas (Scheduler) configurado
- [ ] Logs estructurados generándose

---

## 🐛 Solución de Problemas (Troubleshooting)

### Problema: "No module named 'app'"

```powershell
# Asegúrate de estar en el directorio del backend
cd c:\Proyectos\Automatizaciones\APP\backend
# Y que el entorno virtual esté activado
.\venv\Scripts\Activate.ps1
```

### Problema: "Connection refused" (Redis)

```powershell
# Verificar si Redis está corriendo
docker ps | Select-String redis
# Si no, iniciarlo
docker run -d -p 6379:6379 redis:alpine
```

### Problema: "GEMINI_API_KEY not found"

```powershell
# Verificar .env
Get-Content .env | Select-String GEMINI
# Debe mostrar: GEMINI_API_KEY=tu_key_aqui
```

### Problema: "AUTOMATIC1111 failed"

- Es normal si no tienes SD instalado
- El sistema usa fallback con imágenes negras
- Para probar todo el flujo, instala A1111

### Problema: "Celery worker not responding"

```powershell
# Reiniciar worker
# Ctrl+C en terminal de Celery
celery -A app.core.celery_app worker --pool=solo -l info
```

---

## 📊 Métricas de Éxito

Un sistema funcionando correctamente debería mostrar:

- ✅ **Tiempo de Respuesta de API**: < 100ms para endpoints de lectura
- ✅ **Generación de Guion**: 2-5 segundos con Gemini
- ✅ **Generación de Imágenes**: 10-30 segundos por imagen (con A1111)
- ✅ **Ensamblaje de Video**: 30-60 segundos para video de 15s
- ✅ **Tasa de Acierto de Caché (Hit Rate)**: > 50% en segundo uso
- ✅ **Tasa de Paso de Pruebas (Pass Rate)**: 100% (con configuración completa)

---

## 🎓 Próximos Pasos

Después de verificar que todo funciona:

1. **Personalizar Configuración**
   - Ajustar perfiles de canal
   - Configurar reglas de programación (scheduling)
   - Añadir plantillas personalizadas

2. **Integrar Plataformas**
   - Configurar YouTube OAuth
   - Probar publicación real
   - Configurar TikTok/Instagram

3. **Optimizar Rendimiento**
   - Ajustar workers de Celery
   - Implementar estrategias de caché
   - Migrar a PostgreSQL

4. **Desplegar a Producción**
   - Configurar Docker Compose
   - Configurar monitorización (Grafana)
   - Implementar copias de seguridad automáticas
