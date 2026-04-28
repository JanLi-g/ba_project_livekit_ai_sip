<#
.SYNOPSIS
    Docker Stats Collector fuer Evaluation
.DESCRIPTION
    Erfasst CPU, RAM, Netzwerk fuer alle Docker-Container
#>

param(
    [int]$IntervalSeconds = 5,
    [int]$DurationMinutes = 10,
    [string]$OutputPath = ".\analysis\raw\docker_stats.csv"
)

$ErrorActionPreference = "Stop"

# Output-Verzeichnis erstellen
$outputDir = Split-Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

Write-Host "Docker Stats Collector fuer Evaluation" -ForegroundColor Cyan
Write-Host "   Interval: $IntervalSeconds s | Dauer: $DurationMinutes min" -ForegroundColor Gray
Write-Host "   Output: $OutputPath" -ForegroundColor Gray
Write-Host ""

# CSV Header
$header = "timestamp,container_name,cpu_percent,mem_usage_mb,mem_limit_mb,mem_percent,net_input_mb,net_output_mb"

# Neue Datei mit Header erstellen
$header | Out-File -FilePath $OutputPath -Encoding UTF8

$iterations = ($DurationMinutes * 60) / $IntervalSeconds
$count = 0

Write-Host "Starte Messung... (Strg+C zum Beenden)" -ForegroundColor Green
Write-Host ""

while ($count -lt $iterations) {
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"

    # Docker stats im no-stream Modus
    $stats = docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}}" 2>$null

    if ($stats) {
        foreach ($line in $stats) {
            $parts = $line -split ","
            if ($parts.Count -ge 5) {
                $containerName = $parts[0]
                $cpuPercent = $parts[1] -replace '%', ''

                # Memory parsing
                $memParts = $parts[2] -split " / "
                $memUsage = 0
                $memLimit = 0

                $memUsageStr = $memParts[0]
                if ($memUsageStr -match "(\d+\.?\d*)") {
                    $memUsage = [double]$Matches[1]
                    if ($memUsageStr -like "*GiB*") { $memUsage = $memUsage * 1024 }
                }

                $memLimitStr = $memParts[1]
                if ($memLimitStr -match "(\d+\.?\d*)") {
                    $memLimit = [double]$Matches[1]
                    if ($memLimitStr -like "*GiB*") { $memLimit = $memLimit * 1024 }
                }

                $memPercent = $parts[3] -replace '%', ''

                # Network I/O parsing
                $netParts = $parts[4] -split " / "
                $netInput = 0
                $netOutput = 0

                $netInStr = $netParts[0]
                if ($netInStr -match "(\d+\.?\d*)") {
                    $netInput = [double]$Matches[1]
                    if ($netInStr -like "*GB*") { $netInput = $netInput * 1024 }
                    if ($netInStr -like "*kB*") { $netInput = $netInput / 1024 }
                }

                if ($netParts.Count -gt 1) {
                    $netOutStr = $netParts[1]
                    if ($netOutStr -match "(\d+\.?\d*)") {
                        $netOutput = [double]$Matches[1]
                        if ($netOutStr -like "*GB*") { $netOutput = $netOutput * 1024 }
                        if ($netOutStr -like "*kB*") { $netOutput = $netOutput / 1024 }
                    }
                }

                # CSV Zeile schreiben
                $memUsageR = [math]::Round($memUsage, 2)
                $memLimitR = [math]::Round($memLimit, 2)
                $netInputR = [math]::Round($netInput, 2)
                $netOutputR = [math]::Round($netOutput, 2)

                $csvLine = "$timestamp,$containerName,$cpuPercent,$memUsageR,$memLimitR,$memPercent,$netInputR,$netOutputR"
                $csvLine | Out-File -FilePath $OutputPath -Encoding UTF8 -Append
            }
        }

        $progress = [math]::Round(($count / $iterations) * 100)
        Write-Host "[$progress%] $timestamp - Container erfasst" -ForegroundColor Yellow
    }

    Start-Sleep -Seconds $IntervalSeconds
    $count++
}

Write-Host ""
Write-Host "Messung abgeschlossen!" -ForegroundColor Green
Write-Host "   Datei: $OutputPath" -ForegroundColor Gray

# Statistik
if (Test-Path $OutputPath) {
    $data = Import-Csv $OutputPath
    $containers = ($data | Select-Object -ExpandProperty container_name -Unique) -join ", "
    $dataCount = $data.Count
    Write-Host "   Container: $containers" -ForegroundColor Gray
    Write-Host "   Datenpunkte: $dataCount" -ForegroundColor Gray
}

