# LiveKit Voice Agent Setup Script
Write-Host ""
Write-Host "🚀 LiveKit Voice Agent Setup" -ForegroundColor Green
Write-Host ""
# Schritt 1: Node.js Dependencies
Write-Host "📦 Schritt 1: Node.js Dependencies installieren..." -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Fehler" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js Dependencies installiert" -ForegroundColor Green
Write-Host ""
# Schritt 2: Python prüfen
Write-Host "🐍 Schritt 2: Python-Installation prüfen..." -ForegroundColor Cyan
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVer = python --version 2>&1
    Write-Host "✅ Python gefunden: $pythonVer" -ForegroundColor Green
    Write-Host "📦 Python Dependencies installieren..." -ForegroundColor Cyan
    python -m pip install -r requirements.txt 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python Dependencies installiert" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Hinweis: Python Dependencies später installieren mit:" -ForegroundColor Yellow
        Write-Host "   python -m pip install -r requirements.txt" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  Python nicht gefunden" -ForegroundColor Yellow
    Write-Host "   Installieren Sie Python 3.9+ von https://www.python.org" -ForegroundColor Gray
}
Write-Host ""
# Schritt 3: Docker prüfen  
Write-Host "🐳 Schritt 3: Docker-Installation prüfen..." -ForegroundColor Cyan
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    $dockerVer = docker --version 2>&1
    Write-Host "✅ Docker gefunden: $dockerVer" -ForegroundColor Green
    Write-Host "   Starten mit: docker compose up -d" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Docker nicht gefunden (optional)" -ForegroundColor Yellow
    Write-Host "   Download: https://www.docker.com/products/docker-desktop" -ForegroundColor Gray
}
Write-Host ""
# Schritt 4: Config prüfen
Write-Host "⚙️  Schritt 4: Konfiguration prüfen..." -ForegroundColor Cyan
if (Test-Path ".env.local") {
    Write-Host "✅ .env.local existiert" -ForegroundColor Green
    $envContent = Get-Content ".env.local" -Raw
    if ($envContent -match "your_openai_api_key_here") {
        Write-Host "⚠️  OpenAI API Key noch nicht eingetragen!" -ForegroundColor Yellow
        Write-Host "   Bitte bearbeiten Sie .env.local" -ForegroundColor Gray
    } else {
        Write-Host "✅ OpenAI API Key konfiguriert" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  .env.local nicht gefunden" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "✨ Setup abgeschlossen!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Nächste Schritte:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  OpenAI API Key eintragen:" -ForegroundColor White
Write-Host "   Bearbeiten Sie .env.local und fügen Sie Ihren API Key ein" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  LiveKit Server starten:" -ForegroundColor White
Write-Host "   docker compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Agent Worker starten:" -ForegroundColor White
Write-Host "   python python/agent_worker.py dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Next.js starten:" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "5️⃣  Browser öffnen:" -ForegroundColor White
Write-Host "   http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Siehe auch: QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""
