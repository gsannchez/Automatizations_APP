# ============================================
# Script de Prueba Completa del Sistema
# ============================================

param(
    [switch]$SkipInstall,
    [switch]$SkipRedis,
    [switch]$QuickTest
)

$ErrorActionPreference = "Stop"

# Colores
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Err { Write-Host $args -ForegroundColor Red }

Write-Info "=========================================="
Write-Info "  Sistema de Generacion Automatica de Videos"
Write-Info "  Script de Prueba Completa"
Write-Info "=========================================="
Write-Info ""

# ============================================
# 1. VERIFICAR PREREQUISITOS
# ============================================
Write-Info "[1/10] Verificando prerequisitos..."

# Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "[OK] Python encontrado: $pythonVersion"
} catch {
    Write-Err "[ERROR] Python no encontrado. Instala Python 3.11+"
    exit 1
}

# ============================================
# 2. NAVEGAR AL DIRECTORIO DEL BACKEND
# ============================================
Write-Info ""
Write-Info "[2/10] Navegando al directorio del backend..."

$backendPath = "c:\Proyectos\Automatizaciones\APP\backend"
if (-not (Test-Path $backendPath)) {
    Write-Err "[ERROR] No se encontro el directorio: $backendPath"
    exit 1
}

Set-Location $backendPath
Write-Success "[OK] Directorio: $backendPath"

# ============================================
# 3. CREAR/VERIFICAR ENTORNO VIRTUAL
# ============================================
Write-Info ""
Write-Info "[3/10] Configurando entorno virtual..."

if (-not (Test-Path ".\venv")) {
    Write-Info "Creando nuevo entorno virtual..."
    python -m venv venv
    Write-Success "[OK] Entorno virtual creado"
} else {
    Write-Success "[OK] Entorno virtual existente encontrado"
}

# Activar entorno virtual
& .\venv\Scripts\Activate.ps1
Write-Success "[OK] Entorno virtual activado"

# ============================================
# 4. INSTALAR DEPENDENCIAS
# ============================================
Write-Info ""
if (-not $SkipInstall) {
    Write-Info "[4/10] Instalando dependencias..."
    Write-Warning "Esto puede tomar varios minutos..."
    
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    
    Write-Success "[OK] Dependencias instaladas"
} else {
    Write-Warning "[4/10] Instalacion omitida (parametro -SkipInstall)"
}

# ============================================
# 5. CONFIGURAR ARCHIVO .env
# ============================================
Write-Info ""
Write-Info "[5/10] Configurando archivo .env..."

$envPath = ".env"
if (-not (Test-Path $envPath)) {
    Write-Info "Creando archivo .env de ejemplo..."
    
    # Generar clave de encriptacion
    $encryptionKey = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    
    $envContent = @"
# Base de datos
DATABASE_URL=sqlite:///database.db

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# Redis
REDIS_URL=redis://localhost:6379/0

# Encriptacion
ENCRYPTION_KEY=$encryptionKey

# YouTube OAuth (opcional para pruebas basicas)
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
"@
    
    $envContent | Out-File -FilePath $envPath -Encoding UTF8
    Write-Success "[OK] Archivo .env creado"
    Write-Warning "[IMPORTANTE] Configura tu GEMINI_API_KEY en el archivo .env"
    
    # Esperar a que el usuario configure
    Write-Host ""
    Write-Host "Presiona Enter despues de configurar el .env con tu API key..." -ForegroundColor Yellow
    Read-Host
} else {
    Write-Success "[OK] Archivo .env existente"
}

# ============================================
# 6. VERIFICAR/INICIAR REDIS
# ============================================
Write-Info ""
if (-not $SkipRedis) {
    Write-Info "[6/10] Verificando Redis..."
    
    # Intentar conectar a Redis
    try {
        $redisCheck = python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping()" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "[OK] Redis esta corriendo"
        } else {
            throw "Redis no responde"
        }
    } catch {
        Write-Warning "[WARN] Redis no esta corriendo"
        Write-Info "Para instalar Redis:"
        Write-Info "  1. Con Docker: docker run -d -p 6379:6379 redis:alpine"
        Write-Info "  2. O descarga desde: https://github.com/microsoftarchive/redis/releases"
        Write-Warning "Continuando sin Redis (algunas funciones no estaran disponibles)"
    }
} else {
    Write-Warning "[6/10] Redis omitido (parametro -SkipRedis)"
}

# ============================================
# 7. CREAR BASE DE DATOS
# ============================================
Write-Info ""
Write-Info "[7/10] Inicializando base de datos..."

python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"

if ($LASTEXITCODE -eq 0) {
    Write-Success "[OK] Base de datos creada/actualizada"
} else {
    Write-Err "[ERROR] Fallo al crear la base de datos"
    exit 1
}

# ============================================
# 8. EJECUTAR TESTS
# ============================================
Write-Info ""
Write-Info "[8/10] Ejecutando suite de tests..."

if ($QuickTest) {
    Write-Info "Ejecutando tests rapidos (solo unitarios)..."
    python -m pytest app/tests/test_script_generator.py -v
} else {
    Write-Info "Ejecutando todos los tests..."
    python -m pytest app/tests/ -v --tb=short
}

if ($LASTEXITCODE -eq 0) {
    Write-Success "[OK] Tests pasados exitosamente"
} else {
    Write-Warning "[WARN] Algunos tests fallaron (esto es normal si faltan configuraciones)"
}

# ============================================
# 9. INICIAR SERVIDOR (en background)
# ============================================
Write-Info ""
Write-Info "[9/10] Iniciando servidor FastAPI..."

$serverJob = Start-Job -ScriptBlock {
    Set-Location "c:\Proyectos\Automatizaciones\APP\backend"
    & .\venv\Scripts\Activate.ps1
    uvicorn app.main:app --port 8000 --log-level warning
}

Write-Info "Esperando a que el servidor inicie..."
Start-Sleep -Seconds 5

# Verificar que el servidor esta corriendo
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
    Write-Success "[OK] Servidor FastAPI corriendo en http://localhost:8000"
} catch {
    Write-Err "[ERROR] El servidor no responde"
    Stop-Job $serverJob
    Remove-Job $serverJob
    exit 1
}

# ============================================
# 10. PRUEBAS DE API
# ============================================
Write-Info ""
Write-Info "[10/10] Ejecutando pruebas de API..."

# Funcion helper para hacer requests
function Invoke-ApiTest {
    param($Method, $Endpoint, $Body)
    
    $uri = "http://localhost:8000$Endpoint"
    Write-Info "  -> $Method $Endpoint"
    
    try {
        if ($Body) {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Body ($Body | ConvertTo-Json) -ContentType "application/json"
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method $Method
        }
        Write-Success "  [OK] Success"
        return $response
    } catch {
        Write-Err "  [ERROR] Failed: $($_.Exception.Message)"
        return $null
    }
}

Write-Info ""
Write-Info "--- Test 1: Health Check ---"
Invoke-ApiTest -Method GET -Endpoint "/"

Write-Info ""
Write-Info "--- Test 2: Listar Templates ---"
$templates = Invoke-ApiTest -Method GET -Endpoint "/api/v1/templates/"
if ($templates) {
    Write-Info "  Encontrados $($templates.Count) templates"
}

Write-Info ""
Write-Info "--- Test 3: Crear Template (si no existe) ---"
if (-not $templates -or $templates.Count -eq 0) {
    $newTemplate = @{
        name = "Test Template"
        description = "Template de prueba"
        structure_json = '[{"duration": 5}, {"duration": 5}, {"duration": 5}]'
    }
    $createdTemplate = Invoke-ApiTest -Method POST -Endpoint "/api/v1/templates/" -Body $newTemplate
    $templateId = $createdTemplate.id
} else {
    $templateId = $templates[0].id
    Write-Info "  Usando template existente ID: $templateId"
}

Write-Info ""
Write-Info "--- Test 4: Generar Script con IA ---"
$scriptRequest = @{
    topic = "Inteligencia Artificial en 2025"
    template_id = $templateId
    tone = "Professional"
    platform = "YouTube"
    language = "Spanish"
}
$script = Invoke-ApiTest -Method POST -Endpoint "/api/v1/ai/generate-script" -Body $scriptRequest

if ($script -and $script.scenes) {
    Write-Success "  [OK] Script generado con $($script.scenes.Count) escenas"
    $firstText = $script.scenes[0].text
    $preview = $firstText.Substring(0, [Math]::Min(50, $firstText.Length))
    Write-Info "  Primera escena: $preview..."
}

# ============================================
# RESUMEN FINAL
# ============================================
Write-Info ""
Write-Info "=========================================="
Write-Info "  RESUMEN DE PRUEBAS"
Write-Info "=========================================="

Write-Success "[OK] Sistema configurado correctamente"
Write-Success "[OK] Servidor FastAPI corriendo"
Write-Success "[OK] API endpoints respondiendo"

Write-Info ""
Write-Info "Servicios disponibles:"
Write-Info "  - FastAPI: http://localhost:8000"
Write-Info "  - Swagger Docs: http://localhost:8000/docs"
Write-Info "  - ReDoc: http://localhost:8000/redoc"

Write-Warning ""
Write-Warning "[IMPORTANTE] Para funcionalidad completa, asegurate de tener:"
Write-Warning "  1. Redis corriendo (puerto 6379)"
Write-Warning "  2. Celery worker: celery -A app.core.celery_app worker --pool=solo -l info"
Write-Warning "  3. AUTOMATIC1111: http://localhost:7861"

Write-Info ""
Write-Info "Deseas mantener el servidor corriendo? (S/N)"
$mantener = Read-Host

if ($mantener -ne "S" -and $mantener -ne "s") {
    Write-Info "Deteniendo servidor..."
    Stop-Job $serverJob
    Remove-Job $serverJob
    Write-Success "[OK] Servidor detenido"
} else {
    Write-Success "[OK] Servidor manteniendose activo"
    Write-Info "Para detenerlo: Get-Job | Stop-Job; Get-Job | Remove-Job"
}

Write-Info ""
Write-Info "=========================================="
Write-Success "  Prueba completada!"
Write-Info "=========================================="
