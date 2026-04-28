# ========================================
# LiveKit Voice Agent mit SIP - Vollstaendiger Start
# ========================================

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  LiveKit Voice Agent - SIP Integration (Plusnet)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Pruefe Docker
Write-Host "[DOCKER] Pruefe Docker..." -ForegroundColor Yellow
$dockerRunning = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerRunning) {
    Write-Host "[ERROR] Docker Desktop laeuft nicht!" -ForegroundColor Red
    Write-Host "   Bitte starte Docker Desktop zuerst." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Docker laeuft" -ForegroundColor Green

# Pruefe Python
Write-Host "[PYTHON] Pruefe Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python nicht gefunden!" -ForegroundColor Red
    Write-Host "   Bitte installiere Python 3.10+" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] $pythonVersion" -ForegroundColor Green

# Pruefe .env.local
Write-Host "[CONFIG] Pruefe Konfiguration..." -ForegroundColor Yellow
if (-not (Test-Path ".env.local")) {
    Write-Host "[ERROR] .env.local nicht gefunden!" -ForegroundColor Red
    exit 1
}

# Lade .env.local und pruefe wichtige Variablen
$envContent = Get-Content ".env.local"
$hasOpenAI = $envContent -match "OPENAI_API_KEY=sk-"
$hasSIP = $envContent -match "SIP_PROVIDER_USERNAME="

if (-not $hasOpenAI) {
    Write-Host "[WARNING] OPENAI_API_KEY fehlt oder ist ungueltig" -ForegroundColor Yellow
}
if (-not $hasSIP) {
    Write-Host "[WARNING] SIP Provider Credentials fehlen" -ForegroundColor Yellow
}
Write-Host "[OK] Konfiguration geladen" -ForegroundColor Green

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Schritt 1: Starte Docker Container" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Starte Docker Container
Write-Host "[DOCKER] Starte LiveKit Server, SIP Bridge und Redis..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker Container konnten nicht gestartet werden!" -ForegroundColor Red
    exit 1
}

# Warte auf LiveKit
Write-Host "[WAIT] Warte 5 Sekunden bis LiveKit bereit ist..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Pruefe ob Container laufen
Write-Host "[STATUS] Docker Container Status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Schritt 2: Konfiguriere SIP-Bridge" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Registriere SIP-Trunk und erstelle Dispatch Rules
Write-Host "[SIP] Registriere Plusnet SIP-Trunk und erstelle Routing-Regeln..." -ForegroundColor Yellow
python python/setup_sip_bridge.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] SIP-Bridge Setup fehlgeschlagen!" -ForegroundColor Red
    Write-Host "   Pruefe die Logs mit: docker logs livekit-sip" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Schritt 3: Starte Voice Agent Worker" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[AGENT] Der Voice Agent Worker wird jetzt gestartet..." -ForegroundColor Yellow
Write-Host "   (Der Worker laeuft im Vordergrund und zeigt Logs)" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Zum Beenden: Strg+C druecken" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  [OK] SYSTEM LAEUFT!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "[PHONE] Rufnummer: +49 341 98983401" -ForegroundColor Green
Write-Host "[STATUS] Bereit fuer eingehende Anrufe" -ForegroundColor Green
Write-Host ""
Write-Host "[MONITORING] Verfuegbare Dienste:" -ForegroundColor Cyan
Write-Host "   * LiveKit: http://localhost:7880" -ForegroundColor White
Write-Host "   * Docker Logs: docker logs livekit-sip -f" -ForegroundColor White
Write-Host "   * Agent Logs: siehe unten" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Starte Agent Worker im Vordergrund
python python/agent_worker.py

