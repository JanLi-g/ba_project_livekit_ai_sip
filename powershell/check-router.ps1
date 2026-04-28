#!/usr/bin/env pwsh
# Quick Check: Router-Situation und Port-Forwarding

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Router & Port-Forwarding Check" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Öffentliche IP
Write-Host "[1/3] Prüfe öffentliche IP..." -ForegroundColor Yellow
try {
    $publicIP = Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 5
    Write-Host "   Öffentliche IP: $publicIP" -ForegroundColor Green
} catch {
    Write-Host "   FEHLER: Konnte öffentliche IP nicht abrufen" -ForegroundColor Red
    $publicIP = "UNKNOWN"
}

Write-Host ""

# 2. Lokale IP
Write-Host "[2/3] Prüfe lokale IP..." -ForegroundColor Yellow
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress
Write-Host "   Lokale IP: $localIP" -ForegroundColor Green

Write-Host ""

# 3. Firewall-Regeln
Write-Host "[3/3] Prüfe Windows Firewall-Regeln..." -ForegroundColor Yellow
$rules = Get-NetFirewallRule -DisplayName "*Asterisk*","*LiveKit*" -ErrorAction SilentlyContinue | Where-Object {$_.Enabled -eq $true}
if ($rules) {
    Write-Host "   ✅ Firewall-Regeln gefunden:" -ForegroundColor Green
    $rules | ForEach-Object {
        Write-Host "      - $($_.DisplayName)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️  KEINE Firewall-Regeln gefunden!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Analyse
if ($publicIP -eq $localIP) {
    Write-Host "✅ ERGEBNIS: Direkt am Internet verbunden!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Deine IP ($publicIP) ist direkt erreichbar." -ForegroundColor White
    Write-Host "   Kein Router Port-Forwarding nötig!" -ForegroundColor White
    Write-Host ""
    Write-Host "   ➡️  Weiter mit Fonial IP-Endgerät Setup!" -ForegroundColor Cyan
} elseif ($localIP -like "192.168.*" -or $localIP -like "10.*" -or $localIP -like "172.*") {
    Write-Host "⚠️  ERGEBNIS: Hinter einem Router!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Öffentliche IP: $publicIP" -ForegroundColor White
    Write-Host "   Lokale IP:      $localIP" -ForegroundColor White
    Write-Host ""
    Write-Host "   ❗ DU BRAUCHST ROUTER PORT-FORWARDING!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Im Router einrichten:" -ForegroundColor Cyan
    Write-Host "   - Port 5061/UDP → $localIP`:5061" -ForegroundColor Gray
    Write-Host "   - Port 5060/UDP → $localIP`:5060" -ForegroundColor Gray
    Write-Host "   - Ports 10000-10100/UDP → $localIP`:10000-10100" -ForegroundColor Gray
    Write-Host "   - Ports 10200-10299/UDP → $localIP`:10200-10299" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Router-Admin meist unter: http://192.168.1.1" -ForegroundColor Gray
    Write-Host "   Suche nach: 'Port Forwarding' oder 'NAT'" -ForegroundColor Gray
} else {
    Write-Host "❓ ERGEBNIS: Unbekannte Konfiguration" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Öffentliche IP: $publicIP" -ForegroundColor White
    Write-Host "   Lokale IP:      $localIP" -ForegroundColor White
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Druecke Enter zum Beenden"

