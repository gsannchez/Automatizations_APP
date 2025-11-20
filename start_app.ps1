$root = $PSScriptRoot

Write-Host "Starting Backend..."
Start-Process powershell -ArgumentList "-NoExit", "-File", "$root\backend\run_backend.ps1"

Write-Host "Starting Frontend Server..."
# We run npm start directly to ensure we are in the right directory
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend\auto-video-frontend'; npm start"

Write-Host "Waiting for Frontend to initialize (15s)..."
Start-Sleep -Seconds 15

Write-Host "Starting Electron..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend\auto-video-frontend'; npm run electron"

Write-Host "All components launched."
