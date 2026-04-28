# Firewall-Setup fuer LiveKit SIP-Telefonie
# Dieses Script oeffnet alle notwendigen Ports fuer externe SIP-Anrufe

Write-Host "LiveKit SIP Firewall Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Administrator-Rechte pruefen
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[FEHLER] Dieses Script benoetigt Administrator-Rechte!" -ForegroundColor Red
    Write-Host "Rechtsklick auf PowerShell -> 'Als Administrator ausfuehren'" -ForegroundColor Yellow
    Read-Host "Druecke Enter zum Beenden"
    exit 1
}

Write-Host "[OK] Administrator-Rechte erkannt" -ForegroundColor Green
Write-Host ""

# Funktion zum Entfernen alter Regeln
function Remove-OldFirewallRule {
    param($RuleName)

    $existingRule = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
    if ($existingRule) {
        Write-Host "[INFO] Entferne alte Regel: $RuleName" -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName $RuleName
    }
}

# Funktion zum Hinzufügen neuer Regeln
function Add-FirewallRule {
    param($Name, $Port, $Protocol, $Description)

    Remove-OldFirewallRule -RuleName $Name

    Write-Host "[+] Erstelle Regel: $Name ($Protocol $Port)" -ForegroundColor Cyan

    try {
        New-NetFirewallRule `
            -DisplayName $Name `
            -Direction Inbound `
            -Action Allow `
            -Protocol $Protocol `
            -LocalPort $Port `
            -Description $Description `
            -ErrorAction Stop | Out-Null

        Write-Host "   [OK] Erfolgreich" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "   [FEHLER] $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "Erstelle Firewall-Regeln..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$totalCount = 0

# 1. SIP Signaling (UDP 5060)
Write-Host "[1/6] SIP Signaling Port" -ForegroundColor Magenta
$totalCount++
if (Add-FirewallRule `
    -Name "LiveKit SIP Signaling" `
    -Port 5060 `
    -Protocol UDP `
    -Description "LiveKit SIP Server - Eingehende Telefon-Anrufe (Signaling)") {
    $successCount++
}
Write-Host ""

# 2. SIP RTP Media (UDP 10000-10100)
Write-Host "[2/6] SIP RTP Media Ports" -ForegroundColor Magenta
$totalCount++
if (Add-FirewallRule `
    -Name "LiveKit SIP RTP Media" `
    -Port "10000-10100" `
    -Protocol UDP `
    -Description "LiveKit SIP - Audio/Video Streams (RTP)") {
    $successCount++
}
Write-Host ""

# 3. LiveKit RTC (UDP 50000-50100)
Write-Host "[3/6] LiveKit RTC Ports" -ForegroundColor Magenta
$totalCount++
if (Add-FirewallRule `
    -Name "LiveKit RTC Port Range" `
    -Port "50000-50100" `
    -Protocol UDP `
    -Description "LiveKit Server - WebRTC Media Streams") {
    $successCount++
}
Write-Host ""

# 4. LiveKit HTTP/WebSocket (TCP 7880)
Write-Host "[4/6] LiveKit HTTP/WebSocket" -ForegroundColor Magenta
$totalCount++
if (Add-FirewallRule `
    -Name "LiveKit HTTP WebSocket" `
    -Port 7880 `
    -Protocol TCP `
    -Description "LiveKit Server - HTTP/WebSocket API") {
    $successCount++
}
Write-Host ""

# 5. LiveKit TURN TCP (TCP 7881)
Write-Host "[5/6] LiveKit TURN (TCP)" -ForegroundColor Magenta
$totalCount++
if (Add-FirewallRule `
    -Name "LiveKit TURN TCP" `
    -Port 7881 `
    -Protocol TCP `
    -Description "LiveKit Server - TURN Server (TCP)") {
    $successCount++
}
Write-Host ""

# 6. LiveKit STUN/TURN UDP (UDP 7882)
Write-Host "[6/6] LiveKit STUN/TURN (UDP)" -ForegroundColor Magenta
$totalCount++
if (Add-FirewallRule `
    -Name "LiveKit STUN TURN UDP" `
    -Port 7882 `
    -Protocol UDP `
    -Description "LiveKit Server - STUN/TURN Server (UDP)") {
    $successCount++
}
Write-Host ""

# Zusammenfassung
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Zusammenfassung" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

if ($successCount -eq $totalCount) {
    Write-Host "[OK] Alle $successCount/$totalCount Firewall-Regeln erfolgreich erstellt!" -ForegroundColor Green
} else {
    $failedCount = $totalCount - $successCount
    Write-Host "[WARNUNG] $successCount/$totalCount Regeln erfolgreich, $failedCount fehlgeschlagen" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Erstellte Regeln anzeigen:" -ForegroundColor Cyan
Write-Host "   Get-NetFirewallRule | Where-Object DisplayName -like 'LiveKit*'" -ForegroundColor Gray
Write-Host ""

# Aktuelle Regeln anzeigen
Write-Host "Aktive LiveKit Firewall-Regeln:" -ForegroundColor Cyan
Write-Host ""
Get-NetFirewallRule | Where-Object DisplayName -like 'LiveKit*' |
    Select-Object DisplayName, Enabled, Direction, Action |
    Format-Table -AutoSize

Write-Host ""
Write-Host "[FERTIG] Setup abgeschlossen!" -ForegroundColor Green
Write-Host ""
Write-Host "Naechster Schritt:" -ForegroundColor Yellow
Write-Host "   .\start-all.ps1  # System starten" -ForegroundColor White
Write-Host ""

Read-Host "Druecke Enter zum Beenden"

