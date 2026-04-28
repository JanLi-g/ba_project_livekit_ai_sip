# WebUI Call Testing Script
# Testet 30 Web-UI Anrufe (kurz/mittel/lang)

$baseUrl = "http://localhost:3000"
$csvFile = "evaluation/results/webui_calls.csv"
$logDir = "evaluation/logs"

# Header anlegen falls Datei nicht existiert
if (-not (Test-Path $csvFile)) {
    "call_id,category,prompt,start_time,e2e_latency_ms,mos,intelligibility,naturalness,artifacts_type,cpu_percent,ram_mb,notes,transcript_delay_ms" | Out-File -FilePath $csvFile -Encoding utf8
}

# Prompts definieren
$shortPrompts = @(
    "Wie ist das aktuelle Wetter?",
    "Was ist heute fuer Datum?",
    "Wie heisst du?",
    "Was kannst du mir sagen?",
    "Gruess mich freundlich"
)

$mediumPrompts = @(
    "Erklaere mir die Funktionsweise eines Sprachmodells in 30 Sekunden.",
    "Was sind die Vorteile und Nachteile von Cloud-Computing?",
    "Wie funktioniert eine SIP-Bridge in der Telefonie?",
    "Beschreibe den Unterschied zwischen WebRTC und SIP.",
    "Was ist eine Voice Activity Detection und warum ist sie wichtig?",
    "Erz ahle mir eine kurze Geschichte ueber Kuenstliche Intelligenz."
)

$longPrompts = @(
    "Fasse die Architektur eines modernen Voice-Agent Systems zusammen, inklusive Komponenten, Datenfluss und Herausforderungen.",
    "Erlaeutere die Challenges bei der Integration von LLMs in SIP-basierte Telefonsysteme unter Beruecksichtigung von Latenz, Skalierung und Datenschutz."
)

# Function zum Abrufen der Systemmetriken
function Get-SystemMetrics {
    $cpu = (Get-WmiObject win32_processor | Select-Object LoadPercentage).LoadPercentage
    $ram = [Math]::Round((Get-WmiObject Win32_OperatingSystem | Select-Object @{Name="UsedMemory";Expression={[Int64]($_.TotalVisibleMemorySize-$_.FreePhysicalMemory)/1024}}).UsedMemory)

    return @{
        cpu = $cpu
        ram = $ram
    }
}

# Create evaluation logs dir if not exists
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# Header anlegen falls Datei leer ist
if (-not (Test-Path $csvFile)) {
    "call_id,category,prompt,start_time,e2e_latency_ms,mos,intelligibility,naturalness,artifacts_type,cpu_percent,ram_mb,notes,transcript_delay_ms" | Out-File -FilePath $csvFile -Encoding utf8
}

Write-Host "======================================================================"
Write-Host "WebUI Call Testing - 30 Calls (Kurz/Mittel/Lang)"
Write-Host "======================================================================"
Write-Host ""

$callCounter = 1

# PHASE 1: Kurz-Prompts (10 Calls)
Write-Host "PHASE 1: Kurz-Prompts (10 Calls)" -ForegroundColor Green
Write-Host "Dauer: ca. 15 Minuten (30 Sek pro Call + 30 Sek Pause)"
Write-Host ""

for ($i = 0; $i -lt 10; $i++) {
    $prompt = $shortPrompts[$i % $shortPrompts.Length]
    $callId = $("{0:000}" -f $callCounter)
    Write-Host "[$callId] KURZ | $prompt"
    Write-Host "  Oeffne Browser: $baseUrl"
    Write-Host "  Spreche Prompt ins Mikrofon"
    Write-Host "  Warte auf Agent-Antwort"
    Write-Host "  >>> Druecke ENTER, wenn die Antwort komplett angekommen ist"
    Read-Host | Out-Null
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fff"

    # Automatisch erfassen; Felder fuer spaetere Auswertung leer lassen (MOS/E2E/Artefakte)
    $mos = ""
    $artifacts = ""
    $e2e = ""
    $intelligibility = ""
    $naturalness = ""
    $notes = ""
    $transcriptDelay = ""  # wird spaeter per merge_metrics.py ergänzt

    $metrics = Get-SystemMetrics

    # CSV-Zeile erstellen
    $csvLine = "$callId,short,""$prompt"",$timestamp,$e2e,$mos,$intelligibility,$naturalness,$artifacts,$($metrics.cpu),$($metrics.ram),$notes,$transcriptDelay"

    # In CSV speichern
    Add-Content -Path $csvFile -Value $csvLine

    Write-Host "  OK gespeichert in $csvFile"
    Write-Host "  Pause 30 Sekunden..."
    Write-Host ""

    Start-Sleep -Seconds 30
    $callCounter++
}

# PHASE 2: Mittel-Prompts (15 Calls)
Write-Host ""
Write-Host "PHASE 2: Mittel-Prompts (15 Calls)" -ForegroundColor Green
Write-Host "Dauer: ca. 25 Minuten"
Write-Host ""

for ($i = 0; $i -lt 15; $i++) {
    $prompt = $mediumPrompts[$i % $mediumPrompts.Length]
    $callId = $("{0:000}" -f $callCounter)
    Write-Host "[$callId] MITTEL | $prompt"
    Write-Host "  Oeffne Browser: $baseUrl"
    Write-Host "  Spreche Prompt ins Mikrofon"
    Write-Host "  Warte auf Agent-Antwort"
    Write-Host "  >>> Druecke ENTER, wenn die Antwort komplett angekommen ist"
    Read-Host | Out-Null
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fff"

    $mos = ""
    $artifacts = ""
    $e2e = ""
    $intelligibility = ""
    $naturalness = ""
    $notes = ""
    $transcriptDelay = ""

    $metrics = Get-SystemMetrics

    $csvLine = "$callId,medium,""$prompt"",$timestamp,$e2e,$mos,$intelligibility,$naturalness,$artifacts,$($metrics.cpu),$($metrics.ram),$notes,$transcriptDelay"
    Add-Content -Path $csvFile -Value $csvLine

    Write-Host "  OK gespeichert"
    Write-Host "  Pause 30 Sekunden..."
    Write-Host ""

    Start-Sleep -Seconds 30
    $callCounter++
}

# PHASE 3: Lang-Prompts (5 Calls)
Write-Host ""
Write-Host "PHASE 3: Lang-Prompts (5 Calls)" -ForegroundColor Green
Write-Host "Dauer: ca. 10 Minuten"
Write-Host ""

for ($i = 0; $i -lt 5; $i++) {
    $prompt = $longPrompts[$i % $longPrompts.Length]
    $callId = $("{0:000}" -f $callCounter)
    Write-Host "[$callId] LANG | $($prompt.Substring(0, [Math]::Min(60, $prompt.Length)))..."
    Write-Host "  Oeffne Browser: $baseUrl"
    Write-Host "  Spreche Prompt ins Mikrofon"
    Write-Host "  Warte auf Agent-Antwort"
    Write-Host "  >>> Druecke ENTER, wenn die Antwort komplett angekommen ist"
    Read-Host | Out-Null
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fff"

    $mos = ""
    $artifacts = ""
    $e2e = ""
    $intelligibility = ""
    $naturalness = ""
    $notes = ""
    $transcriptDelay = ""

    $metrics = Get-SystemMetrics

    $csvLine = "$callId,long,""$prompt"",$timestamp,$e2e,$mos,$intelligibility,$naturalness,$artifacts,$($metrics.cpu),$($metrics.ram),$notes,$transcriptDelay"
    Add-Content -Path $csvFile -Value $csvLine

    Write-Host "  OK gespeichert"
    Write-Host "  Pause 30 Sekunden..."
    Write-Host ""

    Start-Sleep -Seconds 30
    $callCounter++
}

Write-Host ""
Write-Host "======================================================================"
Write-Host "OK ALLE 30 CALLS DURCHGEFUEHRT!"
Write-Host "======================================================================"
Write-Host ""
Write-Host "Naechste Schritte:"
Write-Host "1. python evaluate/analyze_results.py --webui"
Write-Host "2. Ergebnisse in Kapitel 6 eintragen"
Write-Host ""
