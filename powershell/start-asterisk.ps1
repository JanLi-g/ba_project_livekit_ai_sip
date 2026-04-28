#!/usr/bin/env pwsh
# Startet das komplette System mit Asterisk SIP Bridge

$dockerPath = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"
$dockerComposePath = "C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe"

Write-Host ""
Write-Host "Asterisk SIP Bridge System starten..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor DarkGray
Write-Host ""

# Pruefe Docker
$dockerDesktop = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerDesktop) {
    Write-Host "[FEHLER] Docker Desktop laeuft nicht!" -ForegroundColor Red
    Write-Host "Bitte Docker Desktop starten und dann erneut versuchen." -ForegroundColor Yellow
    Read-Host "Enter zum Beenden"
    exit 1
}

Write-Host "[OK] Docker Desktop laeuft" -ForegroundColor Green
Write-Host ""

# Container starten
Write-Host "[1/3] Starte Docker Container..." -ForegroundColor Yellow
& $dockerComposePath up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   [OK] Container gestartet" -ForegroundColor Green
} else {
    Write-Host "   [FEHLER] Container konnten nicht gestartet werden" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "   [WARTE] Warte auf Container-Start (10 Sekunden)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Container-Status
Write-Host ""
Write-Host "[2/3] Pruefe Container-Status..." -ForegroundColor Yellow
& $dockerPath ps --format "table {{.Names}}\t{{.Status}}"

Write-Host ""
Write-Host "[3/3] Pruefe Asterisk-Registrierung..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$asteriskLogs = & $dockerPath logs untitled-asterisk-1 2>&1 | Select-String "register" -CaseSensitive:$false

if ($asteriskLogs) {
    Write-Host ""
    Write-Host "Asterisk-Registrierungs-Status:" -ForegroundColor Cyan
    $asteriskLogs | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    Write-Host ""

    if ($asteriskLogs -match "Successfully") {
        Write-Host "[OK] Asterisk ist bei Plusnet registriert!" -ForegroundColor Green
    } else {
        Write-Host "[WARNUNG] Registrierung moeglicherweise fehlgeschlagen" -ForegroundColor Yellow
        Write-Host "Pruefe Logs: docker logs untitled-asterisk-1" -ForegroundColor Gray
    }
} else {
    Write-Host "[INFO] Noch keine Registrierungs-Logs" -ForegroundColor Yellow
    Write-Host "Warte 30 Sekunden und pruefe erneut..." -ForegroundColor Gray
}

Write-Host ""
Write-Host "======================================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "[OK] System gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "Naechste Schritte:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Agent Worker starten (neues Terminal):" -ForegroundColor White
Write-Host "   python python/agent_worker.py dev" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Next.js starten (optional, neues Terminal):" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Testen:" -ForegroundColor White
Write-Host "   Rufe an: +49 341 98983401" -ForegroundColor Yellow
Write-Host ""
Write-Host "Logs ansehen:" -ForegroundColor Cyan
Write-Host "   docker logs -f untitled-asterisk-1  # Asterisk" -ForegroundColor Gray
Write-Host "   docker logs -f untitled-livekit-sip-1  # LiveKit SIP" -ForegroundColor Gray
Write-Host ""

Read-Host "Druecke Enter zum Beenden"
