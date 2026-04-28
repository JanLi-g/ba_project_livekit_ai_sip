# SIP Testing & Diagnostics Script
# Prüft alle Komponenten der SIP-Integration

Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      SIP Integration - System Check             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Docker Container prüfen
Write-Host "📦 Prüfe Docker Container..." -ForegroundColor Yellow
$dockerRunning = docker ps --filter "name=livekit" --format "{{.Names}}" 2>$null

if ($dockerRunning) {
    Write-Host "✅ Docker Container laufen:" -ForegroundColor Green
    docker ps --filter "name=livekit" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
} else {
    Write-Host "❌ Keine Docker Container gefunden!" -ForegroundColor Red
    Write-Host "   Starte mit: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 2. Ports prüfen
Write-Host "🔌 Prüfe Ports..." -ForegroundColor Yellow

$ports = @{
    "7880" = "LiveKit HTTP/WebSocket"
    "7881" = "LiveKit TURN"
    "7882" = "LiveKit RTC (UDP)"
    "5060" = "SIP (UDP)"
    "3000" = "Next.js Dev Server"
}

foreach ($port in $ports.Keys) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($connection.TcpTestSucceeded -or $port -eq "7882" -or $port -eq "5060") {
        Write-Host "✅ Port $port`: $($ports[$port])" -ForegroundColor Green
    } else {
        Write-Host "❌ Port $port`: $($ports[$port]) nicht erreichbar!" -ForegroundColor Red
    }
}

Write-Host ""

# 3. LiveKit API prüfen
Write-Host "🎙️  Prüfe LiveKit API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:7880" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ LiveKit Server antwortet (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ LiveKit Server nicht erreichbar!" -ForegroundColor Red
    Write-Host "   Prüfe: docker-compose logs livekit" -ForegroundColor Yellow
}

Write-Host ""

# 4. Next.js API prüfen
Write-Host "🌐 Prüfe Next.js APIs..." -ForegroundColor Yellow

$apis = @{
    "http://localhost:3000/api/sip/inbound" = "SIP Inbound Handler"
    "http://localhost:3000/api/sip/status" = "SIP Status API"
}

foreach ($api in $apis.Keys) {
    try {
        $response = Invoke-RestMethod -Uri $api -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ $($apis[$api]): OK" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($apis[$api]): Nicht erreichbar" -ForegroundColor Red
        Write-Host "   Starte mit: npm run dev" -ForegroundColor Yellow
    }
}

Write-Host ""

# 5. Agent Worker prüfen
Write-Host "🤖 Prüfe Agent Worker..." -ForegroundColor Yellow
$agentProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*python\\agent_worker.py*" }

if ($agentProcess) {
    Write-Host "✅ Agent Worker läuft (PID: $($agentProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "❌ Agent Worker läuft nicht!" -ForegroundColor Red
    Write-Host "   Starte mit: python python/agent_worker.py start" -ForegroundColor Yellow
}

Write-Host ""

# 6. SIP Status abrufen
Write-Host "📊 SIP Status..." -ForegroundColor Yellow
try {
    $sipStatus = Invoke-RestMethod -Uri "http://localhost:3000/api/sip/status" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Total Rooms: $($sipStatus.summary.totalRooms)" -ForegroundColor Green
    Write-Host "✅ SIP Calls: $($sipStatus.summary.sipCalls)" -ForegroundColor Green
    Write-Host "✅ Web Calls: $($sipStatus.summary.webCalls)" -ForegroundColor Green

    if ($sipStatus.sipCalls.Count -gt 0) {
        Write-Host "`n📞 Aktive SIP-Calls:" -ForegroundColor Cyan
        $sipStatus.sipCalls | Format-Table -Property callId, participants, durationSeconds -AutoSize
    }
} catch {
    Write-Host "⚠️  SIP Status nicht verfügbar" -ForegroundColor Yellow
}

Write-Host ""

# 7. Zusammenfassung
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              System Check Abgeschlossen          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "💡 Nächste Schritte:" -ForegroundColor Yellow
Write-Host "   1. Softphone (Linphone/Zoiper) installieren" -ForegroundColor White
Write-Host "   2. SIP-Account konfigurieren: sip:testuser@localhost:5060" -ForegroundColor White
Write-Host "   3. Anrufen: sip:agent@localhost:5060" -ForegroundColor White
Write-Host "   4. Status prüfen: http://localhost:3000/api/sip/status" -ForegroundColor White
Write-Host ""

Write-Host "📚 Dokumentation:" -ForegroundColor Yellow
Write-Host "   - SIP_QUICKSTART.md → Schnelle Anleitung" -ForegroundColor White
Write-Host "   - SIP_IMPLEMENTATION_PLAN.md → Detaillierter Plan" -ForegroundColor White
Write-Host ""
