# Quick Check: Router-Situation und Port-Forwarding

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Router & Port-Forwarding Check" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Oeffentliche IP
Write-Host "[1/3] Pruefe oeffentliche IP..." -ForegroundColor Yellow
try {
    $publicIP = Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 5
    Write-Host "   Oeffentliche IP: $publicIP" -ForegroundColor Green
} catch {
    Write-Host "   FEHLER: Konnte oeffentliche IP nicht abrufen" -ForegroundColor Red
    $publicIP = "UNKNOWN"
}

Write-Host ""

# 2. Lokale IP
Write-Host "[2/3] Pruefe lokale IP..." -ForegroundColor Yellow
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress
Write-Host "   Lokale IP: $localIP" -ForegroundColor Green

Write-Host ""

# 3. Firewall-Regeln
Write-Host "[3/3] Pruefe Windows Firewall-Regeln..." -ForegroundColor Yellow
$rules = Get-NetFirewallRule -DisplayName "*Asterisk*","*LiveKit*" -ErrorAction SilentlyContinue | Where-Object {$_.Enabled -eq $true}
if ($rules) {
    Write-Host "   OK Firewall-Regeln gefunden:" -ForegroundColor Green
    $rules | ForEach-Object {
        Write-Host "      - $($_.DisplayName)" -ForegroundColor Gray
    }
} else {
    Write-Host "   WARNUNG: KEINE Firewall-Regeln gefunden!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Analyse
if ($publicIP -eq $localIP) {
    Write-Host "OK ERGEBNIS: Direkt am Internet verbunden!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Deine IP ($publicIP) ist direkt erreichbar." -ForegroundColor White
    Write-Host "   Kein Router Port-Forwarding noetig!" -ForegroundColor White
    Write-Host ""
    Write-Host "   Weiter mit Fonial IP-Endgeraet Setup!" -ForegroundColor Cyan
} elseif ($localIP -like "192.168.*" -or $localIP -like "10.*" -or $localIP -like "172.*") {
    Write-Host "WARNUNG: ERGEBNIS: Hinter einem Router!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Oeffentliche IP: $publicIP" -ForegroundColor White
    Write-Host "   Lokale IP:      $localIP" -ForegroundColor White
    Write-Host ""
    Write-Host "   DU BRAUCHST ROUTER PORT-FORWARDING!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Im Router einrichten:" -ForegroundColor Cyan
    Write-Host "   - Port 5061/UDP -> ${localIP}:5061" -ForegroundColor Gray
    Write-Host "   - Port 5060/UDP -> ${localIP}:5060" -ForegroundColor Gray
    Write-Host "   - Ports 10000-10100/UDP -> ${localIP}:10000-10100" -ForegroundColor Gray
    Write-Host "   - Ports 10200-10299/UDP -> ${localIP}:10200-10299" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   Router-Admin meist unter: http://192.168.1.1" -ForegroundColor Gray
    Write-Host "   Suche nach: Port Forwarding oder NAT" -ForegroundColor Gray
} else {
    Write-Host "UNBEKANNT: ERGEBNIS: Unbekannte Konfiguration" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Oeffentliche IP: $publicIP" -ForegroundColor White
    Write-Host "   Lokale IP:      $localIP" -ForegroundColor White
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

