# LiveKit Starter
Write-Host ""
Write-Host "🚀 Starte LiveKit Server..." -ForegroundColor Green
# Docker-Pfad hinzufugen
$env:Path += ";C:\Program Files\Docker\Docker\resources\bin"
# Starte LiveKit
Set-Location $PSScriptRoot
docker compose up -d
if ($LASTEXITCODE -eq 0) {
    Start-Sleep -Seconds 3
    Write-Host ""
    Write-Host "✅ LiveKit Server lauft!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Status:" -ForegroundColor Cyan
    docker compose ps
    Write-Host ""
    Write-Host "Logs:" -ForegroundColor Cyan
    docker compose logs --tail=10
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
    Write-Host "LiveKit: ws://localhost:7880" -ForegroundColor White
    Write-Host ""
    Write-Host "Nachste Schritte:" -ForegroundColor Cyan
    Write-Host "1. python python/agent_worker.py dev" -ForegroundColor Gray
    Write-Host "2. npm run dev" -ForegroundColor Gray
    Write-Host "3. Browser: http://localhost:3000" -ForegroundColor Gray
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
} else {
    Write-Host "❌ Fehler beim Starten!" -ForegroundColor Red
}
Write-Host ""
