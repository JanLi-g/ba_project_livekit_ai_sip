# PowerShell Script zum Konvertieren aller Akronyme im Glossar

$glossaryPath = "E:\WebstormProjects\untitled\thesis\glossary.tex"
$content = Get-Content $glossaryPath -Raw -Encoding UTF8

# Liste aller Akronyme (aus acronyms.tex)
$acronyms = @(
    "PABX", "DPIA", "GDPR", "MANO", "BPO", "EIA", "ALSA", "HTTP", "ARI", "VM", "RFC",
    "IETF", "DID", "NDJSON", "PESQ", "POLQA", "PCM", "TCP", "RTC", "PJSIP", "UDP", "JWT",
    "RMS", "DTMF", "DACH", "HTTPS", "NLP", "ISO", "VLAN", "KMS", "DSGVO", "PCM16", "STUN",
    "TURN", "RTP-Bridge", "KMU", "SIP", "LLM", "WebRTC", "VoIP", "KI", "AI", "API", "RTP",
    "RTCP", "SRTP", "DTLS", "NAT", "ICE", "ASR", "STT", "TTS", "VAD", "MOS", "ITU-T", "PBX",
    "IVR", "NFV", "ETSI", "VNF", "NFVI", "NFVO", "CDR", "SLA", "RBAC", "TLS", "mTLS", "DPA",
    "SCC", "QoS", "PII", "CPaaS", "SFU", "CPU", "RAM", "JSON", "SDK", "CLI", "REST", "UI",
    "PSTN", "OSS", "SPA", "E2E", "RAG", "MEC", "TTL", "YAML", "LAN", "AVV", "ALSA", "ARI",
    "NDJSON", "DACH", "ISO"
)

# Funktion zum Extrahieren der Langform aus description
function Get-LongForm($description, $acronym) {
    # Versuche, die erste Langform zu finden
    $pattern = "([A-Za-z\s\(\)\-\/]+?),\s"
    if ($description -match $pattern) {
        $longForm = $matches[1].Trim()
        # Entferne Klammern und extra Leerzeichen
        $longForm = $longForm -replace '\s+', ' ' -replace '\(.*?\)', ''
        return $longForm.Trim()
    }
    return $null
}

# Verarbeite jeden Akronym
foreach ($acronym in $acronyms) {
    # Finde den Glossary-Eintrag für diesen Akronym
    $pattern = "\\newglossaryentry\{gls-$([Regex]::Escape($acronym))\}\{`n\s+type=fachwort,`n\s+name=$acronym,`n\s+description=\{([^\}]+(?:\{[^\}]*\}[^\}]*)*)\}`n\}"

    if ($content -match $pattern) {
        $description = $matches[1]
        $longForm = Get-LongForm $description $acronym

        if ($longForm) {
            Write-Host "Processing: $acronym → $longForm"

            # Erstelle den neuen Eintrag mit first und text
            $oldEntry = $matches[0]
            $newEntry = @"
\newglossaryentry{gls-$acronym}{
  type=fachwort,
  name=$acronym,
  first={$longForm ($acronym)},
  text=$acronym,
  description={$description}
}
"@

            $content = $content -replace [Regex]::Escape($oldEntry), $newEntry
        }
    }
}

Set-Content -Path $glossaryPath -Value $content -Encoding UTF8
Write-Host "Conversion complete!"

