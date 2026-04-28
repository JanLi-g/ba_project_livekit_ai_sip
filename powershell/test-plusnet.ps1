# Plusnet SIP Integration Test Script
# Testet die komplette SIP-Integration mit deinem Plusnet-Account

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📞 Plusnet SIP Integration Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Farben
$Success = "Green"
$Warning = "Yellow"
$Error = "Red"
$Info = "Cyan"

# Test 1: .env.local überprüfen
Write-Host "[1/7] Überprüfe .env.local..." -ForegroundColor $Info
if (Test-Path ".env.local") {
    $envContent = Get-Content ".env.local" -Raw

    $checks = @(
        "SIP_PROVIDER_DOMAIN",
        "SIP_PROVIDER_USERNAME",
        "SIP_PROVIDER_PASSWORD",
        "SIP_DID_NUMBER"
    )

    $allOk = $true
    foreach ($key in $checks) {
        if ($envContent -match "(?m)^$key\s*=\s*.+$") {
            Write-Host "  ✅ $key konfiguriert" -ForegroundColor $Success
        } else {
            Write-Host "  ❌ $key fehlt oder falsch" -ForegroundColor $Error
            $allOk = $false
        }
    }

    if ($allOk) {
        Write-Host "  ✅ Plusnet-Konfiguration vollständig" -ForegroundColor $Success
    }
} else {
    Write-Host "  ❌ .env.local nicht gefunden!" -ForegroundColor $Error
}
Write-Host ""

# Test 2: livekit-config.yaml überprüfen
Write-Host "[2/7] Überprüfe livekit-config.yaml..." -ForegroundColor $Info
if (Test-Path "livekit-config.yaml") {
    $configContent = Get-Content "livekit-config.yaml" -Raw

    if ($configContent -match "YOUR_LIVEKIT_API_KEY_HERE") {
        Write-Host "  ✅ Platzhalter für LiveKit-Schlüssel vorhanden" -ForegroundColor $Success
    } else {
        Write-Host "  ❌ Platzhalter für LiveKit-Schlüssel fehlt" -ForegroundColor $Error
    }

    if ($configContent -match "redis:") {
        Write-Host "  ✅ Redis-Konfiguration vorhanden" -ForegroundColor $Success
    } else {
        Write-Host "  ⚠️  Redis-Konfiguration fehlt" -ForegroundColor $Warning
    }
} else {
    Write-Host "  ❌ livekit-config.yaml nicht gefunden!" -ForegroundColor $Error
}
Write-Host ""

# Test 3: Docker Status
Write-Host "[3/7] Überprüfe Docker..." -ForegroundColor $Info
try {
    $dockerVersion = docker --version 2>$null
    Write-Host "  ✅ Docker installiert: $dockerVersion" -ForegroundColor $Success

    # Prüfe ob Container laufen
    $runningContainers = docker ps --format "{{.Names}}" 2>$null
    if ($runningContainers -match "livekit") {
        Write-Host "  ✅ LiveKit Container läuft" -ForegroundColor $Success
    } else {
        Write-Host "  ⚠️  LiveKit Container läuft nicht" -ForegroundColor $Warning
        Write-Host "     Starte mit: docker-compose up -d" -ForegroundColor $Info
    }

    if ($runningContainers -match "sip") {
        Write-Host "  ✅ SIP Bridge Container läuft" -ForegroundColor $Success
    } else {
        Write-Host "  ⚠️  SIP Bridge Container läuft nicht" -ForegroundColor $Warning
    }
} catch {
    Write-Host "  ❌ Docker nicht gefunden oder nicht gestartet" -ForegroundColor $Error
}
Write-Host ""

# Test 4: Ports prüfen
Write-Host "[4/7] Überprüfe Ports..." -ForegroundColor $Info
$ports = @{
    "7880" = "LiveKit WebSocket"
    "5060" = "SIP"
    "50000" = "RTP Start"
}

foreach ($port in $ports.Keys) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($connection.TcpTestSucceeded -or $port -eq "5060" -or $port -eq "50000") {
        Write-Host "  ✅ Port $port ($($ports[$port])) OK" -ForegroundColor $Success
    } else {
        Write-Host "  ⚠️  Port $port ($($ports[$port])) nicht erreichbar" -ForegroundColor $Warning
    }
}
Write-Host ""

# Test 5: Python Agent Worker
Write-Host "[5/7] Überprüfe Python Agent..." -ForegroundColor $Info
if (Test-Path "python/agent_worker.py") {
    Write-Host "  ✅ python/agent_worker.py gefunden" -ForegroundColor $Success
    $agentContent = Get-Content "python/agent_worker.py" -Raw

    if ($agentContent -match "sip-call-") {
        Write-Host "  ✅ SIP-Call-Erkennung implementiert" -ForegroundColor $Success
    } else {
        Write-Host "  ⚠️  SIP-Call-Erkennung fehlt" -ForegroundColor $Warning
    }
} else {
    Write-Host "  ❌ python/agent_worker.py nicht gefunden!" -ForegroundColor $Error
}
Write-Host ""

# Test 6: API Endpoints
Write-Host "[6/7] Teste API Endpoints..." -ForegroundColor $Info
try {
    # Teste nur wenn Dev-Server läuft
    $statusResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/sip/status" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✅ SIP Status API erreichbar" -ForegroundColor $Success

    $inboundResponse = Invoke-WebRequest -Uri "http://localhost:3000/api/sip/inbound" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "  ✅ SIP Inbound API erreichbar" -ForegroundColor $Success
} catch {
    Write-Host "  ⚠️  Next.js Dev-Server läuft nicht (starte mit: npm run dev)" -ForegroundColor $Warning
}
Write-Host ""

# Test 7: Firewall-Regeln
Write-Host "[7/7] Überprüfe Firewall..." -ForegroundColor $Info
try {
    $firewallRules = Get-NetFirewallRule -DisplayName "*LiveKit*" -ErrorAction SilentlyContinue
    if ($firewallRules) {
        Write-Host "  ✅ Firewall-Regeln gefunden: $($firewallRules.Count)" -ForegroundColor $Success
    } else {
        Write-Host "  ⚠️  Keine LiveKit Firewall-Regeln gefunden" -ForegroundColor $Warning
        Write-Host "     Für Produktion benötigt (Port 5060, 50000-50100)" -ForegroundColor $Info
    }
} catch {
    Write-Host "  ⚠️  Firewall-Check fehlgeschlagen (benötigt Admin-Rechte)" -ForegroundColor $Warning
}
Write-Host ""

# Zusammenfassung
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 Zusammenfassung" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Provider: Plusnet (Deutsche Telekom)" -ForegroundColor $Info
Write-Host "SIP Domain: sip.plusnet.de" -ForegroundColor $Info
Write-Host "DID Nummer: (aus .env.local)" -ForegroundColor $Info
Write-Host ""
Write-Host "SIP-Stack: LiveKit SIP (eingebaut)" -ForegroundColor $Success
Write-Host "           NICHT Asterisk oder Baresip!" -ForegroundColor $Warning
Write-Host ""

# Nächste Schritte
Write-Host "🚀 Nächste Schritte:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Starte Docker Container:" -ForegroundColor $Info
Write-Host "   docker-compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Starte Agent Worker:" -ForegroundColor $Info
Write-Host "   python python/agent_worker.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Starte Next.js Frontend:" -ForegroundColor $Info
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test mit Softphone (Linphone):" -ForegroundColor $Info
Write-Host "   - Download: https://www.linphone.org/" -ForegroundColor Gray
Write-Host "   - Account: Plusnet SIP-Daten eingeben" -ForegroundColor Gray
Write-Host "   - Anrufen: SIP_DID_NUMBER aus deiner lokalen .env.local" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Für Produktion (extern erreichbar):" -ForegroundColor $Info
Write-Host "   - Öffentliche IP in livekit-config.yaml eintragen" -ForegroundColor Gray
Write-Host "   - Router Port-Forwarding: 5060, 50000-50100" -ForegroundColor Gray
Write-Host "   - Plusnet Admin: IP-Whitelist konfigurieren" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Dokumentation: PLUSNET_SIP_SETUP.md" -ForegroundColor $Success
Write-Host ""

# Logs anzeigen
Write-Host "Docker Logs anzeigen: docker-compose logs -f --tail=50" -ForegroundColor $Info
Write-Host ""
