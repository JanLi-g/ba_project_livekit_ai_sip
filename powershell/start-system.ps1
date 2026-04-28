#!/usr/bin/env pwsh
# Docker Start Helper - Startet System mit direktem Docker-Pfad

Write-Host ""
Write-Host "LiveKit Voice Agent System starten..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor DarkGray
Write-Host ""

# Docker-Pfad
$dockerPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
$dockerComposePath = "C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe"

# Pruefe ob Docker Desktop laeuft
$dockerDesktop = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerDesktop) {
    Write-Host "[FEHLER] Docker Desktop laeuft nicht!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bitte starten:" -ForegroundColor Yellow
    Write-Host "1. Windows-Taste druecken" -ForegroundColor White
    Write-Host "2. 'Docker Desktop' tippen und Enter" -ForegroundColor White
    Write-Host "3. Warten bis Docker-Icon in Taskleiste gruen ist" -ForegroundColor White
    Write-Host "4. Dieses Skript erneut ausfuehren" -ForegroundColor White
    Write-Host ""
    Read-Host "Druecke Enter zum Beenden"
    exit 1
}

Write-Host "[OK] Docker Desktop laeuft" -ForegroundColor Green

# Warte bis Docker bereit ist
Write-Host "[WARTE] Pruefe Docker-Bereitschaft..." -ForegroundColor Yellow
$retries = 0
$maxRetries = 10
while ($retries -lt $maxRetries) {
    try {
        & $dockerPath ps 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Docker ist bereit" -ForegroundColor Green
            break
        }
    } catch {
        # Ignoriere Fehler
    }

    $retries++
    if ($retries -lt $maxRetries) {
        Write-Host "   Warte noch $($maxRetries - $retries) Sekunden..." -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if ($retries -eq $maxRetries) {
    Write-Host "[FEHLER] Docker ist nicht bereit" -ForegroundColor Red
    Write-Host "Bitte warte bis Docker Desktop vollstaendig gestartet ist" -ForegroundColor Yellow
    Read-Host "Druecke Enter zum Beenden"
    exit 1
}

Write-Host ""

# Stoppe alte Container
Write-Host "[1/4] Stoppe alte Container..." -ForegroundColor Yellow
& $dockerComposePath down 2>&1 | Out-Null
Write-Host "   [OK] Alte Container gestoppt" -ForegroundColor Green
Start-Sleep -Seconds 1

# Starte neue Container
Write-Host ""
Write-Host "[2/4] Starte Docker Container..." -ForegroundColor Yellow
& $dockerComposePath up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Container gestartet" -ForegroundColor Green
    Write-Host "      - livekit (Port 7880, 7881, 7882, 50000-50100)" -ForegroundColor Gray
    Write-Host "      - livekit-sip (Port 5060, 10000-10100)" -ForegroundColor Gray
} else {
    Write-Host "   [FEHLER] Fehler beim Starten" -ForegroundColor Red
    Write-Host ""
    Write-Host "Docker-Logs:" -ForegroundColor Yellow
    & $dockerComposePath logs --tail=20
    exit 1
}

Write-Host ""
Write-Host "   [WARTE] Warte auf LiveKit Server (5 Sekunden)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Starte Agent Worker im Hintergrund
Write-Host ""
Write-Host "[3/4] Starte Voice Agent..." -ForegroundColor Yellow
$agentJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    python python/agent_worker.py
}
Write-Host "   [OK] Agent Job ID: $($agentJob.Id)" -ForegroundColor Green
Start-Sleep -Seconds 3

# Starte Next.js
Write-Host ""
Write-Host "[4/4] Starte Next.js Development Server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "======================================" -ForegroundColor DarkGray
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
Write-Host "[INFO] Jetzt kannst du +49 341 98983401 anrufen!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Zum Beenden: Strg+C druecken" -ForegroundColor Yellow
Write-Host ""

# Starte npm dev (blockierend)
npm run dev

# Cleanup
Write-Host ""
Write-Host "Raeume auf..." -ForegroundColor Yellow
Stop-Job -Id $agentJob.Id -ErrorAction SilentlyContinue
Remove-Job -Id $agentJob.Id -ErrorAction SilentlyContinue
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "[OK] Fertig!" -ForegroundColor Green
