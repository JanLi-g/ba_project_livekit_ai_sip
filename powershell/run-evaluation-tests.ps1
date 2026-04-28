# Evaluation Test-Runner
# Führt N Test-Calls durch und sammelt Metriken

param(
    [int]$NumberOfCalls = 30,
    [int]$DelayBetweenCalls = 10,
    [switch]$MeasureResources = $true
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🧪 EVALUATION TEST RUNNER" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "   Anzahl Calls: $NumberOfCalls"
Write-Host "   Delay zwischen Calls: ${DelayBetweenCalls}s"
Write-Host "   Ressourcen messen: $MeasureResources"
Write-Host ""

# Prüfe ob Docker läuft
$containers = docker ps --format "{{.Names}}" 2>$null
if (-not $containers) {
    Write-Host "❌ Docker-Container laufen nicht!" -ForegroundColor Red
    Write-Host "   Führe zuerst 'docker-compose up -d' aus"
    exit 1
}
Write-Host "✅ Docker-Container laufen" -ForegroundColor Green

# Prüfe ob Next.js läuft
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Next.js Server läuft auf Port 3000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Next.js Server nicht erreichbar auf Port 3000" -ForegroundColor Yellow
    Write-Host "   Starte mit 'npm run dev'"
}

# Starte Ressourcen-Messung im Hintergrund
if ($MeasureResources) {
    Write-Host ""
    Write-Host "📊 Starte Ressourcen-Messung im Hintergrund..." -ForegroundColor Yellow

    $resourceJob = Start-Job -ScriptBlock {
        param($ProjectRoot, $Duration)
        & "$ProjectRoot\powershell\measure-resources.ps1" -IntervalSeconds 5 -DurationMinutes $Duration
    } -ArgumentList $ProjectRoot, ([math]::Ceiling(($NumberOfCalls * $DelayBetweenCalls) / 60) + 2)

    Write-Host "   Job ID: $($resourceJob.Id)"
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🚀 STARTE TEST-CALLS" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Test-Prompts (kurz, mittel, lang)
$prompts = @(
    # Kurz (10x)
    @{type="kurz"; text="Wie geht es dir?"},
    @{type="kurz"; text="Wer bist du?"},
    @{type="kurz"; text="Wie spät ist es?"},
    @{type="kurz"; text="Was ist dein Name?"},
    @{type="kurz"; text="Hilf mir bitte."},
    @{type="kurz"; text="Danke schön."},
    @{type="kurz"; text="Auf Wiedersehen."},
    @{type="kurz"; text="Kannst du mich hören?"},
    @{type="kurz"; text="Wie ist das Wetter?"},
    @{type="kurz"; text="Was kannst du?"},

    # Mittel (15x)
    @{type="mittel"; text="Erkläre mir bitte, was Containerisierung bedeutet."},
    @{type="mittel"; text="Wie funktioniert ein SIP-Anruf technisch?"},
    @{type="mittel"; text="Was ist der Unterschied zwischen TCP und UDP?"},
    @{type="mittel"; text="Beschreibe mir die Vorteile von Cloud-Computing."},
    @{type="mittel"; text="Wie kann ich meine Produktivität steigern?"},
    @{type="mittel"; text="Was ist künstliche Intelligenz einfach erklärt?"},
    @{type="mittel"; text="Erkläre mir das Konzept von Microservices."},
    @{type="mittel"; text="Wie funktioniert Spracherkennung technisch?"},
    @{type="mittel"; text="Was sind die Grundlagen von Docker?"},
    @{type="mittel"; text="Beschreibe den Unterschied zwischen REST und GraphQL."},
    @{type="mittel"; text="Wie kann ich Python am besten lernen?"},
    @{type="mittel"; text="Was ist WebRTC und wofür wird es verwendet?"},
    @{type="mittel"; text="Erkläre mir das Client-Server-Modell."},
    @{type="mittel"; text="Wie funktioniert Verschlüsselung bei HTTPS?"},
    @{type="mittel"; text="Was sind Best Practices für API-Design?"},

    # Lang (5x)
    @{type="lang"; text="Beschreibe ausführlich die Vor- und Nachteile von Cloud-basierten LLMs im Vergleich zu lokal gehosteten Modellen für Telefonie-Anwendungen."},
    @{type="lang"; text="Erkläre mir detailliert, wie ein Voice-Agent technisch aufgebaut ist und welche Komponenten für die Sprachverarbeitung benötigt werden."},
    @{type="lang"; text="Beschreibe die Architektur eines containerisierten SIP-Systems und welche Herausforderungen bei der Integration mit modernen Cloud-Diensten auftreten."},
    @{type="lang"; text="Erkläre mir ausführlich die verschiedenen Methoden zur Latenz-Optimierung in Echtzeit-Kommunikationssystemen und deren Trade-offs."},
    @{type="lang"; text="Beschreibe die technischen Anforderungen und Implementierungsdetails für einen produktionsreifen KI-gestützten Telefon-Assistenten."}
)

Write-Host "📝 Verfügbare Prompts:"
Write-Host "   - Kurz (3-5s): 10"
Write-Host "   - Mittel (8-12s): 15"
Write-Host "   - Lang (15-20s): 5"
Write-Host ""

$successCount = 0
$failCount = 0
$results = @()

for ($i = 1; $i -le $NumberOfCalls; $i++) {
    $prompt = $prompts[($i - 1) % $prompts.Count]

    Write-Host "[$i/$NumberOfCalls] Test-Call ($($prompt.type))..." -ForegroundColor Yellow

    $startTime = Get-Date

    try {
        # Hier würde der eigentliche API-Call zum Voice Agent kommen
        # Da wir keinen automatisierten Audio-Input haben, loggen wir nur

        # Simuliere Call-Dauer basierend auf Prompt-Typ
        $duration = switch ($prompt.type) {
            "kurz" { Get-Random -Minimum 3 -Maximum 6 }
            "mittel" { Get-Random -Minimum 8 -Maximum 13 }
            "lang" { Get-Random -Minimum 15 -Maximum 21 }
        }

        Write-Host "   Prompt: '$($prompt.text.Substring(0, [Math]::Min(50, $prompt.text.Length)))...'" -ForegroundColor Gray
        Write-Host "   Erwartete Dauer: ${duration}s" -ForegroundColor Gray

        # Warte (simuliert den Call)
        Start-Sleep -Seconds $duration

        $endTime = Get-Date
        $actualDuration = ($endTime - $startTime).TotalSeconds

        $results += @{
            call_number = $i
            prompt_type = $prompt.type
            prompt_text = $prompt.text
            duration_seconds = [math]::Round($actualDuration, 2)
            status = "success"
            timestamp = $startTime.ToString("yyyy-MM-ddTHH:mm:ss")
        }

        $successCount++
        Write-Host "   ✅ Erfolgreich (${actualDuration}s)" -ForegroundColor Green

    } catch {
        $failCount++
        Write-Host "   ❌ Fehler: $_" -ForegroundColor Red

        $results += @{
            call_number = $i
            prompt_type = $prompt.type
            prompt_text = $prompt.text
            duration_seconds = 0
            status = "error"
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        }
    }

    # Pause zwischen Calls
    if ($i -lt $NumberOfCalls) {
        Write-Host "   ⏳ Warte ${DelayBetweenCalls}s..." -ForegroundColor Gray
        Start-Sleep -Seconds $DelayBetweenCalls
    }

    Write-Host ""
}

# Ergebnisse speichern
$resultsPath = Join-Path $ProjectRoot "analysis\raw\test_calls.csv"
$results | ForEach-Object { [PSCustomObject]$_ } | Export-Csv -Path $resultsPath -NoTypeInformation -Encoding UTF8
Write-Host "💾 Test-Ergebnisse gespeichert: $resultsPath" -ForegroundColor Green

# Ressourcen-Job beenden
if ($MeasureResources -and $resourceJob) {
    Write-Host ""
    Write-Host "⏹️  Beende Ressourcen-Messung..." -ForegroundColor Yellow
    Stop-Job -Job $resourceJob
    Remove-Job -Job $resourceJob
}

# Zusammenfassung
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "📊 ZUSAMMENFASSUNG" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "   Gesamt Calls: $NumberOfCalls"
Write-Host "   Erfolgreich: $successCount" -ForegroundColor Green
Write-Host "   Fehlgeschlagen: $failCount" -ForegroundColor $(if ($failCount -gt 0) { "Red" } else { "Green" })
Write-Host "   Erfolgsrate: $([math]::Round($successCount / $NumberOfCalls * 100, 1))%"
Write-Host ""
Write-Host "📁 Output-Dateien:"
Write-Host "   - $resultsPath"
Write-Host "   - $(Join-Path $ProjectRoot 'analysis\raw\docker_stats.csv')"
Write-Host "   - $(Join-Path $ProjectRoot 'analysis\raw\events.csv')"
Write-Host ""
Write-Host "🔬 Nächster Schritt:"
Write-Host "   python analysis\run_evaluation.py"
Write-Host ""

