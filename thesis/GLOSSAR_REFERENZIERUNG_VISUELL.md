# 📚 GLOSSAR-REFERENZIERUNG: Visuelle Übersicht

## 🎯 DEINE SITUATION

Du möchtest:
- ✅ **Nur 1 Glossar** (keine separates Akronym-Register)
- ✅ **Akronyme und Fachwörter** in einem Verzeichnis
- ✅ **Hyperlinks** im Text auf das Glossar
- ✅ **Keine Vorkommen-Markierungen** (kein Index)

---

## 🔄 DIE UMSTELLUNG

```
┌─────────────────────────────────────────────────────────────────┐
│                        VORHER (Aktuell)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Dateien:                                                        │
│  ├── acronyms.tex      (91 Akronyme)                            │
│  ├── glossary.tex      (26 Fachwörter)                          │
│  └── main.tex                                                    │
│      └── \printacronyms        ← KEIN REGISTER!                 │
│      └── \printglossaries                                        │
│                                                                   │
│  Im Text:                                                        │
│  ├── \acrshort{KI}           → "KI" (einfacher Text)           │
│  ├── \acrshort{SIP}          → "SIP" (einfacher Text)          │
│  └── normaler Text für Fachwörter                               │
│                                                                   │
│  PDF-Ausgabe:                                                    │
│  ├── [Seite 5] Akronymverzeichnis ← ENTFERNEN!                 │
│  └── [Seite 7] Glossar (nur Fachwörter)                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓↓↓ UMSTELLUNG ↓↓↓
┌─────────────────────────────────────────────────────────────────┐
│                         NACHHER (Neu)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Dateien:                                                        │
│  ├── glossary.tex      (147 Einträge: 91 + 56)  ✨            │
│  └── main.tex                                                    │
│      └── \printglossaries   ← NUR Glossar!                     │
│                                                                   │
│  Im Text:                                                        │
│  ├── \gls{gls-KI}      → "Künstliche Intelligenz" + Link      │
│  ├── \gls{gls-SIP}     → "Session Initiation Protocol" + Link  │
│  └── \gls{gls-Codec}   → "Codec" + Link (Fachwort)            │
│                                                                   │
│  PDF-Ausgabe:                                                    │
│  └── [Seite 5] Glossar (Akronyme + Fachwörter gemischt) ✨    │
│      - KI: Künstliche Intelligenz                               │
│      - Codec: Encoder-Decoder-Verfahren                         │
│      - SIP: Session Initiation Protocol                         │
│      - ...                                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 KONKRETE ÄNDERUNGEN

### 1️⃣ PREAMBLE (main.tex)

**ENTFERNEN/ÄNDERN:**
```latex
% ❌ ALT - NICHT MEHR VERWENDEN:
\usepackage[acronym]{glossaries}        ← entfernen!
\loadglsentries{thesis/acronyms}        ← entfernen!
```

**HINZUFÜGEN/ÄNDERN:**
```latex
% ✅ NEU - VERWENDEN:
\usepackage[noindex]{glossaries}        ← neu!
\loadglsentries{thesis/glossary}        ← glossary.tex als einzige Quelle
```

---

### 2️⃣ REGISTER AM ENDE (main.tex)

**ENTFERNEN:**
```latex
% ❌ ALT - NICHT MEHR VERWENDEN:
\printacronyms[title=Abkürzungsverzeichnis]
```

**BEHALTEN:**
```latex
% ✅ WEITERVERWENDEN:
\printglossaries
```

---

### 3️⃣ IM TEXT (Alle 8 Kapitel)

**Find & Replace für alle .tex Dateien:**

| Vorher | Nachher |
|--------|---------|
| `\acrshort{KI}` | `\gls{gls-KI}` |
| `\acrshort{SIP}` | `\gls{gls-SIP}` |
| `\acrshort{VoIP}` | `\gls{gls-VoIP}` |
| `\acrshort{RTP}` | `\gls{gls-RTP}` |
| (alle 91 Akronyme) | (mit `gls-` Präfix) |

---

## 💻 AUTOMATISCHE UMSTELLUNG

Falls du es automatisieren möchtest:

### PowerShell-Skript:
```powershell
$files = Get-ChildItem -Path "E:\WebstormProjects\untitled\thesis\0[1-8]_*.tex"

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $content = $content -replace '\\acrshort\{([^}]+)\}', '\gls{gls-$1}'
    Set-Content $file.FullName $content -Encoding UTF8
    Write-Host "Updated: $($file.Name)"
}
```

---

## 📊 AUSWIRKUNGEN AUF DEIN DOKUMENT

### PDF-STRUKTUR

**Vorher:**
```
Inhaltsverzeichnis
├── 1. Einleitung
├── 2. Grundlagen
├── 3. Anforderungen
├── 4. Architektur
├── 5. Marktanalyse
├── 6. Implementierung
├── 7. Evaluation
├── 8. Diskussion
├── Akronymverzeichnis     ← TRENNT TEXT VON BEGRIFFEN
└── Glossar
```

**Nachher:**
```
Inhaltsverzeichnis
├── 1. Einleitung
├── 2. Grundlagen
├── 3. Anforderungen
├── 4. Architektur
├── 5. Marktanalyse
├── 6. Implementierung
├── 7. Evaluation
├── 8. Diskussion
└── Glossar    ✨ ALLES AN EINEM ORT
    (Akronyme + Fachwörter alphabetisch gemischt)
```

### IM LESEN

**Vorher:** "KI wird eingesetzt"
- Leser kennt Akronym nicht → muss rückwärts blättern zum Akronymverzeichnis

**Nachher:** "Künstliche Intelligenz wird eingesetzt" + Hyperlink
- Leser sieht sofort: Das ist "KI" (= Künstliche Intelligenz)
- Kann per Hyperlink zum Glossar springen → Definition sehen

---

## 📋 REFERENZ: `\gls{}` BEFEHLE

### Varianten von Glossar-Referenzen:

```latex
% Normale Referenz (empfohlen):
\gls{gls-KI}              % "Künstliche Intelligenz"

% Mit Custom-Text:
\glstext{gls-KI}          % "KI" (nur Name)

% Plural:
\glspl{gls-KI}            % "Künstliche Intelligenzen"

% First-Use Short (für spezielle Fälle):
\glsuserfirstname{gls-KI} % Nur bei Custom-Einträgen

% Nur Kurz ohne Link (selten nötig):
\acrshort{gls-KI}         % Funktioniert aber → nutze \gls stattdessen!
```

---

## ✨ GLOSSAR-OPTIONEN (Optional)

Falls du noch flexiblere Ausgabe brauchst:

```latex
% In main.tex Preamble:

% Option 1: Einfach (standard):
\usepackage[noindex]{glossaries}

% Option 2: Mit Hyperlinks und Styling:
\usepackage[noindex,colorlinks]{glossaries}

% Option 3: Mit Baum-Struktur (schön!):
\usepackage[noindex]{glossaries}
\usepackage{glossary-tree}

% Option 4: Mit Abteilungen (Akronyme/Fachwörter getrennt):
\usepackage[noindex]{glossaries}
\newglossary[alg]{acronyms}{acr}{acn}{Akronyme}
% Dann in glossary.tex:
\newglossaryentry[acronyms]{gls-KI}{...}
% Aber: Dann wieder separate Register! → Nicht empfohlen für dich!
```

---

## 🎯 MEINE EMPFEHLUNG FÜR DEINE BA

**Am besten:** Einfache Lösung

```latex
% Preamble:
\usepackage[noindex]{glossaries}
\makeglossaries
\loadglsentries{thesis/glossary}

% Im Text überall:
\gls{gls-KI}        % Statt \acrshort{KI}
\gls{gls-SIP}       % Statt \acrshort{SIP}
\gls{gls-Codec}     % Fachwörter genauso

% Am Ende von main.tex:
\printglossaries    % Nur das!
```

**Ergebnis:**
- ✅ Ein sauberes Glossar
- ✅ Alle Begriffe verlinkt
- ✅ Professionsell aussehen
- ✅ Keine redundanten Register
- ✅ Lesbar und konsistent

---

## 🚀 NÄCHSTE SCHRITTE

1. **Dateien vorbereiten:**
   - [ ] glossary.tex prüfen (147 Einträge vorhanden)
   - [ ] acronyms.tex kann gelöscht werden

2. **main.tex anpassen:**
   - [ ] Preamble aktualisieren
   - [ ] `\printacronyms` löschen
   - [ ] `\printglossaries` halten

3. **Alle Kapitel aktualisieren:**
   - [ ] `\acrshort{XXXX}` → `\gls{gls-XXXX}`
   - [ ] Systematisch mit Find & Replace

4. **Test:**
   - [ ] PDF generieren
   - [ ] Glossar sieht gut aus?
   - [ ] Hyperlinks funktionieren?

5. **Final Check:**
   - [ ] Keine Fehler in Log?
   - [ ] Alle Begriffe angezeigt?
   - [ ] Index/Register gelöscht?

---

## ❓ FAQ

**F: Was ist der Unterschied zwischen `\gls{}` und `\acrshort{}`?**
A: `\gls{}` zeigt die Definition aus dem Glossar, `\acrshort{}` nur das Akronym.

**F: Muss ich die glossary.tex ändern?**
A: Nein, deine glossary.tex ist perfekt! Du brauchst sie nur anders zu referenzieren.

**F: Kann ich acronyms.tex löschen?**
A: Ja! Sie wird nicht mehr benötigt. Das Glossar ersetzt sie.

**F: Sehen die Leser trotzdem die Langform?**
A: Ja! `\gls{gls-KI}` zeigt "Künstliche Intelligenz" (die Langform aus dem Glossar).

**F: Funktionieren Hyperlinks im PDF?**
A: Ja! Mit `\gls{}` werden automatisch Hyperlinks erzeugt.

---

## 📞 BRAUCHST DU HILFE?

Möchtest du, dass ich die Umstellung automatisch durchführe? Ich kann:

1. ✅ Alle `\acrshort{}` → `\gls{gls-}` ersetzen
2. ✅ Preamble in main.tex anpassen
3. ✅ acronyms.tex referenzen entfernen
4. ✅ PDF generieren und testen

Sag mir Bescheid, und ich mache es! 🚀

