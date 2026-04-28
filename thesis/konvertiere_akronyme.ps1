# PowerShell Script zur Konvertierung aller Akronyme
$chapters = @(
    'E:\WebstormProjects\untitled\thesis\01_einleitung.tex',
    'E:\WebstormProjects\untitled\thesis\02_grundlagen.tex',
    'E:\WebstormProjects\untitled\thesis\03_anforderungen.tex',
    'E:\WebstormProjects\untitled\thesis\04_architektur.tex',
    'E:\WebstormProjects\untitled\thesis\05_marktanalyse.tex',
    'E:\WebstormProjects\untitled\thesis\06_implementierung.tex',
    'E:\WebstormProjects\untitled\thesis\07_evaluation.tex',
    'E:\WebstormProjects\untitled\thesis\08_diskussion.tex'
)

Write-Host "Starte Konvertierung..." -ForegroundColor Green

foreach ($chapterPath in $chapters) {
    if (Test-Path $chapterPath) {
        $content = Get-Content $chapterPath -Raw -Encoding UTF8
        $newContent = $content -replace '\\acrshort\{([^}]+)\}', '\gls{gls-$$1}'
        Set-Content $chapterPath $newContent -Encoding UTF8
        $name = Split-Path $chapterPath -Leaf
        Write-Host "✓ $name aktualisiert"
    }
}

Write-Host "✓ Fertig!" -ForegroundColor Green

