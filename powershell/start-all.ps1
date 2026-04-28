#!/usr/bin/env pwsh
# Kompletter Start fuer LiveKit Voice Agent System (mit SIP-Telefonie)

Write-Host ""
Write-Host "Starte LiveKit Voice Agent System (SIP-Produktionsmodus)..." -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor DarkGray
Write-Host ""

# 1. Stoppe alte Docker Container
Write-Host "[1/4] Stoppe alte Docker Container..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "   [OK] Alte Container gestoppt" -ForegroundColor Green
Start-Sleep -Seconds 1

# 2. Starte Docker Container (LiveKit + SIP)
Write-Host ""
Write-Host "[2/4] Starte Docker Container (LiveKit + SIP)..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Docker Container gestartet" -ForegroundColor Green
    Write-Host "      - livekit (Port 7880, 7881, 7882, 50000-50100)" -ForegroundColor Gray
    Write-Host "      - livekit-sip (Port 5060, 10000-10100)" -ForegroundColor Gray
} else {
    Write-Host "   [FEHLER] Fehler beim Starten der Container" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "   [WARTE] Warte auf LiveKit Server (5 Sekunden)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 3. Starte Agent im Hintergrund
Write-Host ""
Write-Host "[3/4] Starte Voice Agent im Hintergrund..." -ForegroundColor Yellow
$agentJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python python/agent_worker.py
}
Write-Host "   [OK] Agent Job ID: $($agentJob.Id)" -ForegroundColor Green
Write-Host "      Logs: docker-compose logs -f livekit-sip" -ForegroundColor Gray
Start-Sleep -Seconds 3

# 4. Starte Next.js Dev Server
Write-Host ""
Write-Host "[4/4] Starte Next.js Development Server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "[OK] System gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "SIP-Telefonie aktiv:" -ForegroundColor Cyan
Write-Host "   Rufnummer:   +49 341 98983401" -ForegroundColor White
Write-Host "   Externe IP:  91.41.217.61" -ForegroundColor White
Write-Host "   SIP Port:    5060/UDP" -ForegroundColor White
Write-Host ""
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "   Web:         http://localhost:3000" -ForegroundColor White
Write-Host "   SIP Status:  http://localhost:3000/api/sip/status" -ForegroundColor White
Write-Host "   LiveKit:     ws://localhost:7880" -ForegroundColor White
Write-Host ""
Write-Host "Status pruefen:" -ForegroundColor Cyan
Write-Host "   docker-compose ps              # Container-Status" -ForegroundColor Gray
Write-Host "   docker-compose logs -f livekit-sip  # SIP-Logs" -ForegroundColor Gray
Write-Host ""
Write-Host "[INFO] Jetzt kannst du +49 341 98983401 anrufen!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Zum Beenden: Strg+C druecken" -ForegroundColor Yellow
Write-Host ""

# Starte npm dev (blockierend)
npm run dev

# Cleanup bei Beendigung
Write-Host ""
Write-Host "Raeume auf..." -ForegroundColor Yellow
Stop-Job -Id $agentJob.Id -ErrorAction SilentlyContinue
Remove-Job -Id $agentJob.Id -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "[OK] Fertig!" -ForegroundColor Green
