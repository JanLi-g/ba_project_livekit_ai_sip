#!/usr/bin/env pwsh
# System-Check fuer SIP-Telefonie
# Prueft ob das System bereit ist fuer externe Anrufe

Write-Host ""
Write-Host "LiveKit SIP System Check" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor DarkGray
Write-Host ""

$allGood = $true

# 1. Docker Desktop laeuft?
Write-Host "[1/10] Docker Desktop..." -ForegroundColor Yellow
try {
    docker version 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Docker Desktop laeuft" -ForegroundColor Green
    } else {
        Write-Host "   [FEHLER] Docker Desktop laeuft nicht" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "   [FEHLER] Docker nicht installiert" -ForegroundColor Red
    $allGood = $false
}

# 2. Docker Container laufen?
Write-Host ""
Write-Host "[2/10] Docker Container..." -ForegroundColor Yellow
$containers = docker-compose ps --services --filter "status=running" 2>&1
if ($containers -match "livekit" -and $containers -match "livekit-sip") {
    Write-Host "   [OK] livekit und livekit-sip Container laufen" -ForegroundColor Green
} else {
    Write-Host "   [FEHLER] Container laufen nicht" -ForegroundColor Red
    Write-Host "      Starten mit: docker-compose up -d" -ForegroundColor Yellow
    $allGood = $false
}

# 3. .env.local existiert?
Write-Host ""
Write-Host "[3/10] .env.local Datei..." -ForegroundColor Yellow
if (Test-Path ".env.local") {
    Write-Host "   [OK] .env.local gefunden" -ForegroundColor Green

    # Pruefe OpenAI API Key
    $envContent = Get-Content ".env.local" -Raw
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "   [OK] OpenAI API Key vorhanden" -ForegroundColor Green
    } else {
        Write-Host "   [WARNUNG] OpenAI API Key fehlt oder ungueltig" -ForegroundColor Yellow
        $allGood = $false
    }
} else {
    Write-Host "   [FEHLER] .env.local nicht gefunden" -ForegroundColor Red
    $allGood = $false
}

# 4. livekit-config.yaml korrekt?
Write-Host ""
Write-Host "[4/10] livekit-config.yaml..." -ForegroundColor Yellow
if (Test-Path "livekit-config.yaml") {
    $config = Get-Content "livekit-config.yaml" -Raw
    if ($config -match "91.41.217.61") {
        Write-Host "   [OK] Externe IP konfiguriert (91.41.217.61)" -ForegroundColor Green
    } else {
        Write-Host "   [WARNUNG] Externe IP nicht gefunden" -ForegroundColor Yellow
        $allGood = $false
    }

    if ($config -match "sip.plusnet.de") {
        Write-Host "   [OK] Plusnet SIP Trunk konfiguriert" -ForegroundColor Green
    } else {
        Write-Host "   [WARNUNG] Plusnet SIP Trunk nicht konfiguriert" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [FEHLER] livekit-config.yaml nicht gefunden" -ForegroundColor Red
    $allGood = $false
}

# 5. Port 7880 (LiveKit HTTP) erreichbar?
Write-Host ""
Write-Host "[5/10] Port 7880 (LiveKit HTTP)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:7880" -TimeoutSec 3 -UseBasicParsing 2>&1
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 404) {
        Write-Host "   [OK] LiveKit Server antwortet" -ForegroundColor Green
    } else {
        Write-Host "   [WARNUNG] Unerwarteter Status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   [FEHLER] LiveKit Server nicht erreichbar" -ForegroundColor Red
    $allGood = $false
}

# 6. Port 5060 (SIP) geoeffnet?
Write-Host ""
Write-Host "[6/10] Port 5060 (SIP UDP)..." -ForegroundColor Yellow
$sipPort = Get-NetUDPEndpoint -LocalPort 5060 -ErrorAction SilentlyContinue
if ($sipPort) {
    Write-Host "   [OK] Port 5060/UDP ist offen" -ForegroundColor Green
} else {
    Write-Host "   [WARNUNG] Port 5060/UDP nicht aktiv" -ForegroundColor Yellow
    Write-Host "      Container laufen? docker-compose ps" -ForegroundColor Gray
}

# 7. Firewall-Regeln vorhanden?
Write-Host ""
Write-Host "[7/10] Windows Firewall Regeln..." -ForegroundColor Yellow
$firewallRules = Get-NetFirewallRule -DisplayName "LiveKit*" -ErrorAction SilentlyContinue
if ($firewallRules) {
    $ruleCount = ($firewallRules | Measure-Object).Count
    Write-Host "   [OK] $ruleCount LiveKit Firewall-Regeln gefunden" -ForegroundColor Green
} else {
    Write-Host "   [WARNUNG] Keine Firewall-Regeln gefunden" -ForegroundColor Yellow
    Write-Host "      Erstellen mit: .\setup-firewall.ps1" -ForegroundColor Gray
}

# 8. Python installiert?
Write-Host ""
Write-Host "[8/10] Python Installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host "   [OK] $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "   [FEHLER] Python 3 nicht gefunden" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "   [FEHLER] Python nicht installiert" -ForegroundColor Red
    $allGood = $false
}

# 9. Python Dependencies installiert?
Write-Host ""
Write-Host "[9/10] Python Dependencies..." -ForegroundColor Yellow
try {
    $packages = pip list 2>&1 | Out-String
    if ($packages -match "livekit" -and $packages -match "openai") {
        Write-Host "   [OK] livekit und openai Pakete installiert" -ForegroundColor Green
    } else {
        Write-Host "   [WARNUNG] Fehlende Pakete" -ForegroundColor Yellow
        Write-Host "      Installieren mit: pip install -r requirements.txt" -ForegroundColor Gray
        $allGood = $false
    }
} catch {
    Write-Host "   [WARNUNG] Konnte Dependencies nicht pruefen" -ForegroundColor Yellow
}

# 10. Node.js und npm?
Write-Host ""
Write-Host "[10/10] Node.js und npm..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    $npmVersion = npm --version 2>&1
    if ($nodeVersion -match "v\d+" -and $npmVersion -match "\d+") {
        Write-Host "   [OK] Node.js $nodeVersion, npm $npmVersion" -ForegroundColor Green
    } else {
        Write-Host "   [FEHLER] Node.js/npm nicht gefunden" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "   [FEHLER] Node.js nicht installiert" -ForegroundColor Red
    $allGood = $false
}

# Zusammenfassung
Write-Host ""
Write-Host "====================================" -ForegroundColor DarkGray
Write-Host ""

if ($allGood) {
    Write-Host "[OK] System ist bereit fuer SIP-Telefonie!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Rufnummer: +49 341 98983401" -ForegroundColor Cyan
    Write-Host "Externe IP: 91.41.217.61" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "System starten mit:" -ForegroundColor Yellow
    Write-Host "   .\start-all.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[WARNUNG] System ist noch nicht vollstaendig bereit" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To-Do:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Docker starten:" -ForegroundColor White
    Write-Host "   docker-compose up -d" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Firewall einrichten:" -ForegroundColor White
    Write-Host "   .\setup-firewall.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Python Pakete installieren:" -ForegroundColor White
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Node Pakete installieren:" -ForegroundColor White
    Write-Host "   npm install" -ForegroundColor Gray
    Write-Host ""
}

# Docker Logs Hinweis
Write-Host "Logs checken:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f livekit" -ForegroundColor Gray
Write-Host "   docker-compose logs -f livekit-sip" -ForegroundColor Gray
Write-Host ""

Read-Host "Druecke Enter zum Beenden"

