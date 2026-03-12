# start_services.ps1
Write-Host "Levantando servicios de infraestructura (PostgreSQL y Redis)..." -ForegroundColor Cyan

# Verifica si Docker está corriendo
$dockerStatus = docker info 2>&1
if ($dockerStatus -match "error during connect") {
    Write-Host "❌ Error: Docker Desktop no está corriendo. Por favor inicia Docker Desktop primero." -ForegroundColor Red
    exit 1
}

# Levanta contenedores en segundo plano (detach mode)
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Servicios inicializados correctamente en Docker:" -ForegroundColor Green
    Write-Host "   - PostgreSQL: puerto 5432 (autovideodb, autovideouser)"
    Write-Host "   - Redis: puerto 6379"
    Write-Host ""
    Write-Host "Esperando 5 segundos para que las bases de datos acepten conexiones..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    Write-Host "¡Listo! Ya puedes ejecutar .\start_app.ps1" -ForegroundColor Green
} else {
    Write-Host "❌ Hubo un error al intentar levantar docker-compose." -ForegroundColor Red
}
