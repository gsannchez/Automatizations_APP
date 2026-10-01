# Celery worker - ejecutar desde backend/ (mismo directorio que run_backend.ps1)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$env:PYTHONUTF8 = "1"
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "ERROR: No se encuentra venv en backend\venv. Ejecuta: python -m venv venv" -ForegroundColor Red
    Read-Host "Pulsa Enter para cerrar"
    exit 1
}

Write-Host "Celery worker - colas: cpu_queue, gpu_queue, upload_queue" -ForegroundColor Cyan
Write-Host "Directorio: $PWD" -ForegroundColor DarkGray

& ".\venv\Scripts\python.exe" -m celery -A app.core.celery_app worker `
    --pool=solo `
    -Q cpu_queue,gpu_queue,upload_queue `
    --without-gossip `
    --without-mingle `
    -l info

if ($LASTEXITCODE -ne 0) {
    Write-Host "Celery termino con codigo $LASTEXITCODE" -ForegroundColor Red
    Read-Host "Pulsa Enter para cerrar"
}
