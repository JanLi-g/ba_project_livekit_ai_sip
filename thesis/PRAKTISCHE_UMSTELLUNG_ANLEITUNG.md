# ⚙️ PRAKTISCHE UMSTELLUNG: `\acrshort{}` → `\gls{}`

## 📋 Schritt-für-Schritt Anleitung

---

## SCHRITT 1: Preamble in main.tex anpassen

### ❌ ALTE PREAMBLE:
```latex
\usepackage[acronym]{glossaries}
\usepackage{glossary-mcols}

\makeglossaries

\loadglsentries{thesis/acronyms}
\loadglsentries{thesis/glossary}
```

### ✅ NEUE PREAMBLE:
```latex
% Glossary-Paket (OHNE acronym!)
\usepackage[noindex]{glossaries}
\usepackage{glossary-mcols}

% Glossaries initialisieren
\makeglossaries

% NUR Glossar laden (acronyms.tex nicht mehr nötig!)
\loadglsentries{thesis/glossary}
```

**Erklärung:**
- `noindex` bedeutet: Kein separates Akronym-Register
- `acronym` entfernt, da alles im Glossar ist
- `acronyms.tex` wird nicht mehr benötigt

---

## SCHRITT 2: Am Ende des Dokuments

### ❌ ALTE AUSGABE:
```latex
% Am Ende von main.tex:
\printacronyms[title=Abkürzungsverzeichnis]
\printglossaries
```

### ✅ NEUE AUSGABE:
```latex
% Am Ende von main.tex:
\printglossaries  % Nur Glossar, KEIN Akronym-Register!
```

---

## SCHRITT 3: Alle `\acrshort{}` im Text ersetzen

### Automatische Replacement mit Find & Replace:

**Find:** `\\acrshort\{([^}]+)\}`  
**Replace:** `\\gls{gls-$1}`

Aber WICHTIG: Die Akronym-Namen (z.B. `KI`, `SIP`) müssen mit `gls-` präfix versehen sein!

---

### MANUELLE UMSTELLUNG - Alle Fälle:

#### Fall 1: Einfache Akronyme
```latex
% ALT:
Die \acrshort{KI} ist wichtig.

% NEU:
Die \gls{gls-KI} ist wichtig.
```

#### Fall 2: Akronyme mit Kontext
```latex
% ALT:
Das Session Initiation Protocol (\acrshort{SIP}) definiert...

% NEU:
Das Session Initiation Protocol (\gls{gls-SIP}) definiert...
```

#### Fall 3: Mehrfaches Vorkommen
```latex
% ALT:
\acrshort{KI} wird eingesetzt. Später: \acrshort{KI} wieder verwendet.

% NEU:
\gls{gls-KI} wird eingesetzt. Später: \gls{gls-KI} wieder verwendet.
% Beide verlinken zum Glossar!
```

#### Fall 4: Fachwörter (neu!)
```latex
% ALT: Fachwörter hatten keine spezielle Markierung

% NEU: Fachwörter genauso markieren wie Akronyme
Der \gls{gls-Codec} komprimiert Audio.
Das \gls{gls-Routing} erfolgt automatisch.
Die \gls{gls-Latenz} wird gemessen.
```

---

## 🔍 BEISPIEL: Komplettes Kapitel vorher/nachher

### ❌ VOR der Umstellung (Kapitel 01):

```latex
\chapter{Einleitung}
\label{chap:einleitung}

\section{Motivation und Kontext}

Die Integration von Künstlicher Intelligenz (\acrshort{KI}) 
in Telefonsysteme führt dazu, dass sich Qualität entwickelt. 
Sprachassistenten ermöglichen automatische Spracherkennung. 
Die Integration von Large Language Models (\acrshort{LLM}) 
erweitert diese Funktionen. Dadurch werden natürlichere Dialoge 
möglich, die klassische Telefonie sowie moderne Sprachplattformen 
ergänzen.

Klassische Voice over Internet Protocol (\acrshort{VoIP})-Systeme, 
die auf dem Session Initiation Protocol (\acrshort{SIP})-Protokoll 
basieren, sind häufig stark an spezielle Hardware gebunden.
```

### ✅ NACH der Umstellung (Kapitel 01):

```latex
\chapter{Einleitung}
\label{chap:einleitung}

\section{Motivation und Kontext}

Die Integration von \gls{gls-KI} in Telefonsysteme führt dazu, 
dass sich Qualität entwickelt. Sprachassistenten ermöglichen 
automatische \gls{gls-Spracherkennung}. Die Integration von 
\gls{gls-LLM} erweitert diese Funktionen. Dadurch werden natürlichere 
Dialoge möglich, die klassische Telefonie sowie moderne Sprachplattformen 
ergänzen.

Klassische \gls{gls-VoIP}-Systeme, die auf dem 
\gls{gls-SIP}-Protokoll basieren, sind häufig stark an spezielle 
Hardware gebunden.
```

**Unterschied im PDF:**
- ALT: "KI", "LLM", "VoIP", "SIP" als normaler Text
- NEU: "Künstliche Intelligenz", "Large Language Model", "Voice over Internet Protocol", "Session Initiation Protocol" mit **Hyperlink zum Glossar**

---

## 📊 Mapping: `\acrshort{}` → `\gls{}`

Die wichtigsten Ersetzungen:

```
\acrshort{KI}              → \gls{gls-KI}
\acrshort{AI}              → \gls{gls-AI}
\acrshort{LLM}             → \gls{gls-LLM}
\acrshort{VoIP}            → \gls{gls-VoIP}
\acrshort{SIP}             → \gls{gls-SIP}
\acrshort{KMU}             → \gls{gls-KMU}
\acrshort{API}             → \gls{gls-API}
\acrshort{WebRTC}          → \gls{gls-WebRTC}
\acrshort{RTP}             → \gls{gls-RTP}
\acrshort{SRTP}            → \gls{gls-SRTP}
\acrshort{DTLS}            → \gls{gls-DTLS}
\acrshort{NAT}             → \gls{gls-NAT}
\acrshort{ICE}             → \gls{gls-ICE}
\acrshort{STUN}            → \gls{gls-STUN}
\acrshort{TURN}            → \gls{gls-TURN}
\acrshort{STT}             → \gls{gls-STT}
\acrshort{TTS}             → \gls{gls-TTS}
\acrshort{ASR}             → \gls{gls-ASR}
\acrshort{VAD}             → \gls{gls-VAD}
\acrshort{MOS}             → \gls{gls-MOS}
\acrshort{RFC}             → \gls{gls-RFC}
\acrshort{IETF}            → \gls{gls-IETF}
\acrshort{ETSI}            → \gls{gls-ETSI}
\acrshort{NFV}             → \gls{gls-NFV}
\acrshort{DSGVO}           → \gls{gls-DSGVO}
... und alle anderen 91 Akronyme analog
```

---

## 🛠️ QUICK-FIX mit sed/PowerShell

Wenn du viele Ersetzungen brauchst, kannst du ein Script verwenden:

### PowerShell (Windows):

```powershell
# Alle \acrshort{XXXX} → \gls{gls-XXXX} ersetzen

$files = Get-ChildItem -Path "E:\WebstormProjects\untitled\thesis\*.tex"

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    
    # Pattern: \acrshort{KI} → \gls{gls-KI}
    $content = $content -replace '\\acrshort\{([^}]+)\}', '\gls{gls-$1}'
    
    Set-Content $file.FullName $content
}

Write-Host "Replacement complete!"
```

### Bash (Linux/Mac):

```bash
# Alle .tex Dateien in Kapitel-Ordner
for file in thesis/0*.tex; do
    sed -i 's/\\acrshort{\([^}]*\)}/\\gls{gls-\1}/g' "$file"
done
echo "Replacement complete!"
```

---

## ✅ CHECKLISTE FÜR UMSTELLUNG

- [ ] **Preamble aktualisiert:**
  - [ ] `\usepackage[noindex]{glossaries}` gesetzt
  - [ ] `\usepackage[acronym]{glossaries}` ENTFERNT
  - [ ] `\loadglsentries{thesis/acronyms}` ENTFERNT

- [ ] **Hauptdatei aktualisiert:**
  - [ ] `\printacronyms` ENTFERNT oder AUSKOMMENTIERT
  - [ ] `\printglossaries` bleibt AKTIV

- [ ] **Alle Kapitel aktualisiert:**
  - [ ] Kapitel 01: `\acrshort{}` → `\gls{gls-}`
  - [ ] Kapitel 02: `\acrshort{}` → `\gls{gls-}`
  - [ ] Kapitel 03: `\acrshort{}` → `\gls{gls-}`
  - [ ] Kapitel 04: `\acrshort{}` → `\gls{gls-}`
  - [ ] Kapitel 05: `\acrshort{}` → `\gls{gls-}`
  - [ ] Kapitel 06: `\acrshort{}` → `\gls{gls-}`
  - [ ] Kapitel 07: `\acrshort{}` → `\gls{gls-}`
  - [ ] Kapitel 08: `\acrshort{}` → `\gls{gls-}`

- [ ] **Glossar-Datei:**
  - [ ] glossary.tex mit 147 Einträgen vorhanden
  - [ ] Alle `gls-XXXX` IDs korrekt

- [ ] **Test:**
  - [ ] PDF generiert ohne Fehler
  - [ ] Glossar wird angezeigt
  - [ ] KEIN Akronym-Register sichtbar
  - [ ] Hyperlinks funktionieren

---

## 🎯 WAS SICH ÄNDERT FÜR DICH

### Vorher (mit acronyms.tex und `\acrshort{}`):
```
PDF-Inhaltsverzeichnis:
  - Glossary (Fachwörter)
  - Acronyms (Akronyme - SEPARATES REGISTER!)
  
Im Text:
  "KI wird eingesetzt" (nur Akronym, nicht verlinkt)
```

### Nachher (nur glossary.tex und `\gls{}`):
```
PDF-Inhaltsverzeichnis:
  - Glossary (Akronyme + Fachwörter gemischt)
  
Im Text:
  "Künstliche Intelligenz wird eingesetzt" 
  + Hyperlink zur Glossar-Seite
```

---

## 💡 TIPPS & TRICKS

### Tipp 1: Glossar-Anzeige variieren
```latex
\gls{gls-KI}        % Zeigt: "Künstliche Intelligenz"
\glstext{gls-KI}    % Zeigt: "KI" (nur Name aus Glossar)
\glspl{gls-KI}      % Zeigt: "Künstliche Intelligenzen" (Plural)
```

### Tipp 2: Glossar-Einträge dynamisch
Im Glossar kannst du flexible Einträge definieren:
```latex
% In glossary.tex:
\newglossaryentry{gls-KI-full}{
  type=fachwort,
  name={Künstliche Intelligenz},
  text={KI},  % Das wird mit \gls angezeigt!
  description={...}
}

% Im Text:
\gls{gls-KI-full}  % Zeigt: "KI" mit Glossar-Link
```

### Tipp 3: Nur erstes Vorkommen markieren
```latex
Verwendung von \gls{gls-KI} (erste Erwähnung wird hervorgehoben)
Bei der zweiten Erwähnung von \gls{gls-KI} ist sie nicht mehr hervorgehoben
```

---

## 📝 ZUSAMMENFASSUNG

**Die einfache Regel:**

```
\acrshort{XXXX}  →  \gls{gls-XXXX}
```

**Dann:**
1. Preamble anpassen (noindex)
2. `\printacronyms` auskommentieren
3. PDF generieren
4. Nur ein schönes Glossar sehen ✨

Möchtest du, dass ich die automatische Umstellung durchführe?

