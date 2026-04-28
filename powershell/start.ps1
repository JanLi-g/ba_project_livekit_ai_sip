# Schnellstart-Script für LiveKit Voice Agent
# Startet alle notwendigen Services

Write-Host ""
Write-Host "🚀 LiveKit Voice Agent wird gestartet..." -ForegroundColor Green
Write-Host ""

# Funktion zum Prüfen ob ein Port belegt ist
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
    return $connection
}

# LiveKit Server prüfen
Write-Host "🔍 Prüfe LiveKit Server..." -ForegroundColor Cyan
if (Test-Port 7880) {
    Write-Host "✅ LiveKit Server läuft bereits auf Port 7880" -ForegroundColor Green
} else {
    Write-Host "⚠️  LiveKit Server läuft nicht" -ForegroundColor Yellow
    Write-Host "   Starten mit: docker compose up -d" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Möchten Sie versuchen, LiveKit Server mit Docker zu starten? (j/n)"
    if ($response -in @('j','J','y','Y')) {
        docker compose up -d
        Start-Sleep -Seconds 3
        if (Test-Port 7880) {
            Write-Host "✅ LiveKit Server gestartet" -ForegroundColor Green
        } else {
            Write-Host "❌ LiveKit Server konnte nicht gestartet werden" -ForegroundColor Red
            exit 1
        }
    }
}
Write-Host ""

# Agent Worker starten
Write-Host "🤖 Agent Worker wird gestartet..." -ForegroundColor Cyan
Write-Host "   (öffnet neues Terminal-Fenster)" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host '🤖 Agent Worker' -ForegroundColor Green; python python/agent_worker.py dev"
Start-Sleep -Seconds 2
Write-Host ""

# Next.js Dev Server starten
Write-Host "🛠  Next.js Development Server wird gestartet..." -ForegroundColor Cyan
Write-Host "   (öffnet neues Terminal-Fenster)" -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host '🛠  Next.js Server' -ForegroundColor Green; npm run dev"
Start-Sleep -Seconds 3
Write-Host ""

Write-Host "----------------------------------------------" -ForegroundColor Green
Write-Host "✨ Alle Services wurden gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "🖥  Öffnen Sie Ihren Browser:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "⏹  Zum Beenden: Fenster schließen oder Strg+C" -ForegroundColor Yellow
Write-Host "----------------------------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "Drücken Sie eine Taste zum Beenden..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
