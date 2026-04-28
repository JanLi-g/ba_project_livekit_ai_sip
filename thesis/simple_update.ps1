# Einfaches Script zum Konvertieren der Glossary-Einträge
# Alle Akronyme bekommen first und text Felder

$glossaryPath = "E:\WebstormProjects\untitled\thesis\glossary.tex"
$content = Get-Content $glossaryPath -Raw -Encoding UTF8

# Ersetze alle Glossary-Einträge ohne first/text durch Einträge mit first/text
# Pattern: \newglossaryentry{gls-ACRONYM}{\n  type=fachwort,\n  name=ACRONYM,\n  description=...

# Für jedes Akronym einzeln ersetzen
$mappings = @{
    'KI' = 'Künstliche Intelligenz'
    'SIP' = 'Session Initiation Protocol'
    'VoIP' = 'Voice over Internet Protocol'
    'KMU' = 'kleine und mittelständische Unternehmen'
    'LLM' = 'Large Language Model'
    'API' = 'Application Programming Interface'
}

foreach ($acronym in $mappings.Keys) {
    $longForm = $mappings[$acronym]

    # Suche nach Einträgen OHNE first/text (älteres Format)
    $pattern = "\\newglossaryentry\{gls-$acronym\}\s*\{`n\s+type=fachwort,`n\s+name=$acronym,`n\s+description="

    if ($content -match $pattern) {
        # Füge first und text hinzu
        $replacement = "\newglossaryentry{gls-$acronym}{`n  type=fachwort,`n  name=$acronym,`n  first={$longForm ($acronym)},`n  text=$acronym,`n  description="
        $content = $content -replace $pattern, $replacement
        Write-Host "✓ $acronym: Added first/text"
    } else {
        Write-Host "- $acronym: Already has first/text or not found"
    }
}

Set-Content -Path $glossaryPath -Value $content -Encoding UTF8
Write-Host "✓ Done!"

