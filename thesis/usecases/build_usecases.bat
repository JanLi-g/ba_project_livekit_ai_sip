@echo off
rem Batch: kompiliert alle usecase*.tex in diesem Ordner nach output\
pushd "%~dp0"
if not exist output mkdir output
for %%F in (usecase*.tex) do (
  echo Kompiliere %%F ...
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory output "%%F" > nul
  if errorlevel 1 (
    echo Fehler beim Kompilieren von %%F
  ) else (
    echo Erfolgreich: output\%%~nF.pdf
  )
)
popd
echo Fertig.

