# Python Auto-Installer für Voice Agent
# Führen Sie dieses Script aus, um Python zu installieren

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "🐍 Python Auto-Installer" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

# Prüfe ob Python bereits installiert ist
Write-Host "🔍 Prüfe ob Python bereits installiert ist..." -ForegroundColor Cyan
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue

if ($pythonCheck) {
    $version = python --version 2>&1
    Write-Host "✅ Python ist bereits installiert: $version" -ForegroundColor Green
    Write-Host ""

    $response = Read-Host "Möchten Sie die Dependencies trotzdem installieren? (j/n)"
    if ($response -eq "j" -or $response -eq "J" -or $response -eq "y" -or $response -eq "Y") {
        Write-Host "📦 Installiere Python Dependencies..." -ForegroundColor Cyan
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        Write-Host "✅ Dependencies installiert!" -ForegroundColor Green
    }
    exit 0
}

Write-Host "❌ Python nicht gefunden" -ForegroundColor Yellow
Write-Host ""

# Download Python
Write-Host "📥 Lade Python 3.12.0 herunter..." -ForegroundColor Cyan
$pythonUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
$installerPath = "$env:TEMP\python-3.12.0-installer.exe"

try {
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✅ Download abgeschlossen: $installerPath" -ForegroundColor Green
} catch {
    Write-Host "❌ Download fehlgeschlagen: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bitte laden Sie Python manuell herunter:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "🔧 Starte Python Installation..." -ForegroundColor Cyan
Write-Host "   Dies kann 2-3 Minuten dauern..." -ForegroundColor Gray
Write-Host ""

# Installiere Python (silent mode mit PATH)
$arguments = "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_doc=0"
Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -NoNewWindow

Write-Host ""
Write-Host "✅ Python Installation abgeschlossen!" -ForegroundColor Green
Write-Host ""

# Aktualisiere PATH
Write-Host "🔄 Aktualisiere Umgebungsvariablen..." -ForegroundColor Cyan
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Verifiziere Installation
Start-Sleep -Seconds 2
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue

if ($pythonCheck) {
    $version = python --version 2>&1
    Write-Host "✅ Python erfolgreich installiert: $version" -ForegroundColor Green
    Write-Host ""

    # Installiere Dependencies
    Write-Host "📦 Installiere Python Dependencies..." -ForegroundColor Cyan
    Write-Host ""

    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Alle Dependencies erfolgreich installiert!" -ForegroundColor Green
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
        Write-Host "🎉 Installation abgeschlossen!" -ForegroundColor Green
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
        Write-Host ""
        Write-Host "Sie können jetzt den Agent Worker starten:" -ForegroundColor Cyan
om        Write-Host "  python python/agent_worker.py dev" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "⚠️ Fehler beim Installieren der Dependencies" -ForegroundColor Yellow
        Write-Host "Versuchen Sie manuell:" -ForegroundColor Cyan
        Write-Host "  pip install -r requirements.txt" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️ Python konnte nicht im PATH gefunden werden" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Bitte führen Sie folgende Schritte aus:" -ForegroundColor Cyan
    Write-Host "1. Öffnen Sie eine NEUE PowerShell" -ForegroundColor White
    Write-Host "2. Führen Sie aus: python --version" -ForegroundColor White
    Write-Host "3. Wenn Python funktioniert:" -ForegroundColor White
    Write-Host "   cd C:\Users\janli\WebstormProjects\untitled" -ForegroundColor Gray
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
pause
