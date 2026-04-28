#!/usr/bin/env pwsh
# Start LiveKit Voice Agent

Write-Host ""
Write-Host "Starte LiveKit Voice Agent..." -ForegroundColor Cyan
Write-Host ""

# Pruefe ob .env.local existiert
if (-not (Test-Path ".env.local")) {
    Write-Host "Fehler: .env.local nicht gefunden!" -ForegroundColor Red
    exit 1
}

# Pruefe ob Python installiert ist
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python gefunden: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python nicht gefunden!" -ForegroundColor Red
    exit 1
}

# Starte Agent
Write-Host ""
Write-Host "Verbinde mit LiveKit Server (ws://localhost:7880)..." -ForegroundColor Yellow
Write-Host "Voice Agent wird gestartet..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor DarkGray
Write-Host ""

# Starte den Agent ohne Dev-Mode (wegen Windows Multiprocessing Issues)
python python/agent_worker.py start
