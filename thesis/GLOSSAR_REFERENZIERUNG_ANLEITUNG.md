# Glossar-Referenzierung: Best Practice für deine BA

## Das Problem
Du verwendest aktuell `\acrshort{KI}` für Akronyme, möchtest aber:
- ✅ Kein separates Akronymverzeichnis (Register)
- ✅ Nur Glossar mit Akronymen und Fachwörtern
- ✅ Fachwörter/Akronyme aber sollen im Text verlinkt werden

---

## 📌 Die Lösung: `\gls{}` statt `\acrshort{}`

### Wichtig: Es gibt 3 Varianten

| Befehl | Ausgabe | Glossar-Link | Wann verwenden |
|--------|---------|--------------|----------------|
| `\gls{gls-KI}` | Künstliche Intelligenz | ✓ Ja | **EMPFOHLEN** - Erste Verwendung |
| `\glspl{gls-KI}` | Künstliche Intelligenzen | ✓ Ja | Für Mehrzahl |
| `\glstext{gls-KI}` | KI (nur Name) | ✓ Ja | Wenn du nur das Akronym anzeigen willst |

---

## 🎯 Beste Strategie für deine BA

### **Option 1: Klassische Lösung (EMPFOHLEN)**

```latex
% Erste Erwähnung im Text:
\gls{gls-KI} ist die Abkürzung für Künstliche Intelligenz.

% Folgende Erwähnungen:
\gls{gls-KI} wird vielfach eingesetzt.

% Glossar generiert automatisch:
- Index wird NICHT erstellt (nur visueller Link)
- Glossar zeigt: "KI - Künstliche Intelligenz: [Definition]"
- Im PDF ist es ein Verweis/Hyperlink
```

**Vorteil:** 
- Einfach und konsistent
- Automatische Linkgenerierung
- Keine redundante Textmarkierung
- Saubere PDF-Ausgabe

---

### **Option 2: Unterscheidung zwischen Akronym und Langform**

Wenn du im Text bereits die Langform schreibst:

```latex
% Langform im Text erwähnen und verlinken:
Künstliche Intelligenz (\gls{gls-KI}) ist ...

% Oder nur Akronym mit Glossar:
\gls{gls-KI} werden eingesetzt.
```

---

## ✅ SCHRITT-FÜR-SCHRITT UMSTELLUNG

### Schritt 1: Entferne `\acrshort{}`
```latex
% ALT (nicht mehr verwenden):
\acrshort{KI}

% NEU (verwenden):
\gls{gls-KI}
```

### Schritt 2: Preamble konfigurieren
Stelle sicher, dass in deiner `main.tex` oder Preamble folgendes gesetzt ist:

```latex
% Glossaries laden
\usepackage[style=list]{glossaries}
\usepackage{glossary-tree}

% Glossary initialisieren
\makeglossaries

% Am Ende des Dokuments KEIN Akronym-Register!
% Nur am Ende: \printglossaries
```

### Schritt 3: Im Text verwenden
```latex
\chapter{Einleitung}
\section{Motivation und Kontext}

Die Integration von \gls{gls-KI} in Telefonsysteme...
Das Session Initiation Protocol (\gls{gls-SIP})...
\gls{gls-KMU} mit begrenzter Mitarbeiteranzahl...
```

### Schritt 4: Nur Glossar drucken (KEIN Akronym-Register)
```latex
% In main.tex am Ende:

% NUR das Glossar, NICHT das Akronym-Register
\printglossaries

% NICHT verwenden:
% \printacronyms  % <-- AUSKOMMENTIERT!
```

---

## 🔍 Unterschied: Alte vs. Neue Lösung

### ❌ ALTE LÖSUNG (Akronyme.tex + \acrshort):
```
Dateistruktur:
├── acronyms.tex      ← Separate Akronyme
├── glossary.tex      ← Separate Fachwörter
├── main.tex
│   ├── \printacronyms   ← Akronym-Register (separates Verzeichnis)
│   └── \printglossaries ← Glossar

Ausgabe im PDF:
- [Seite X] Akronymverzeichnis
- [Seite Y] Glossar
- Im Text: \acrshort{KI} → "KI"
```

### ✅ NEUE LÖSUNG (nur Glossar.tex + \gls):
```
Dateistruktur:
├── glossary.tex      ← ALLES (Akronyme + Fachwörter)
├── main.tex
│   └── \printglossaries ← NUR Glossar (kein separates Register!)

Ausgabe im PDF:
- [Seite X] Glossar (mit Akronymen UND Fachwörtern)
- Im Text: \gls{gls-KI} → "Künstliche Intelligenz" + Glossar-Link
```

---

## 📝 PRAKTISCHE BEISPIELE

### Beispiel 1: Akronym mit Langform
```latex
% Szenario: Beim ersten Mal sowohl Akronym als auch Longform zeigen

Die \gls{gls-KI} ist ein wichtiges Feld.
% PDF zeigt: "Künstliche Intelligenz ist ein wichtiges Feld."
% + Hyperlink zum Glossar
```

### Beispiel 2: Nur Akronym (bei Wiederholung)
```latex
% Nach der ersten Erwähnung kannst du einfach wiederverwenden:

\gls{gls-KI} wird vielfach in Systemen eingesetzt.
% PDF zeigt je nach Konfiguration:
% Option A: "Künstliche Intelligenz wird vielfach..."
% Option B: "KI wird vielfach..." (wenn du nur Akronym willst)
```

### Beispiel 3: Fachwort
```latex
Das \gls{gls-Codec} komprimiert Audio.
% PDF zeigt: "Encoder-Decoder-Verfahren komprimiert Audio."
% + Hyperlink zum Glossar
```

---

## ⚙️ GLOSSARY PAKETE - WELCHES SOLL ICH VERWENDEN?

Für deine BA empfehle ich:

```latex
% OPTION 1 (Einfach, empfohlen für BA):
\usepackage[noindex]{glossaries}
\makeglossaries

% OPTION 2 (Mit alphabetischer Sortierung):
\usepackage[noindex, sort=use]{glossaries}
\makeglossaries

% OPTION 3 (Mit Baum-Struktur, professionell):
\usepackage[noindex]{glossaries}
\usepackage{glossary-tree}
\makeglossaries
```

**Wichtig:** `noindex` bedeutet: **KEIN separates Akronym-Register!**

---

## 🔧 UMSTELLUNG CHECKLIST

- [ ] `\acrshort{KI}` → `\gls{gls-KI}` in allen Kapiteln ersetzen
- [ ] `\acrshort{SIP}` → `\gls{gls-SIP}` ersetzen
- [ ] Alle `\acrshort{}` mit systematischer Suche/Ersetzen umwandeln
- [ ] `\printacronyms` **AUSKOMMENTIEREN** oder LÖSCHEN
- [ ] `\printglossaries` bleibt EINKOMMENTIERT
- [ ] Glossary-Paket in Preamble: `\usepackage[noindex]{glossaries}`
- [ ] Testen: PDF generieren und Glossar überprüfen

---

## 📌 WICHTIGE HINWEISE

### Hyperlinks im Glossar
- Mit `\gls{}` werden automatisch Hyperlinks erzeugt
- Im PDF kannst du auf den Glossar-Eintrag klicken
- Es wird keine extra "Verweise"-Seite erstellt

### Sortierung
- Glossar wird alphabetisch sortiert
- Akronyme und Fachwörter gemischt (da alle `type=fachwort`)
- Falls du Akronyme oben haben möchtest, können wir alternative `type` definieren

### Mehrfachverwendung
```latex
% Das funktioniert natürlich:
\gls{gls-KI} und später wieder \gls{gls-KI}
% Nur der erste Treffer wird meist hervorgehoben,
% alle verlinken zum Glossar
```

---

## 🎯 WEITERE TIPPS

### Akronym vs. Langform gezielt kontrollieren

Falls du flexibel sein möchtest, können wir mehrere Glossary-Varianten definieren:

```latex
% In glossary.tex:
\newglossaryentry{gls-KI-short}{
  type=fachwort,
  name=KI,
  description={Künstliche Intelligenz}
}

\newglossaryentry{gls-KI-long}{
  type=fachwort,
  name=Künstliche Intelligenz,
  description={Fähigkeit von Maschinen, intelligente Aufgaben auszuführen}
}

% Im Text:
\gls{gls-KI-short}   % Zeigt: "KI"
\gls{gls-KI-long}    % Zeigt: "Künstliche Intelligenz"
```

---

## 📊 VERGLEICH: Alle Optionen für deine BA

| Lösung | Akronym-Register | Glossar | Empfehlung |
|--------|------------------|---------|-----------|
| `\acrshort{}` + acronyms.tex | ✓ Ja | ✓ Ja | ❌ Redundant |
| `\gls{}` + glossary.tex (noindex) | ✗ Nein | ✓ Ja | ✅ **BESTE LÖSUNG** |
| `\acrfull{}` + acronyms.tex | ✓ Ja | ✗ Nein | ❌ Zu aufdringlich |

---

## ✨ ZUSAMMENFASSUNG

**Deine neue Referenzierungsweise:**

```latex
% ERSETZE ALLE:
\acrshort{KI}       → \gls{gls-KI}
\acrshort{SIP}      → \gls{gls-SIP}
\acrshort{VoIP}     → \gls{gls-VoIP}
% usw.

% Preamble:
\usepackage[noindex]{glossaries}
\makeglossaries

% Am Ende (nur Glossar, kein Register):
\printglossaries
```

**Ergebnis:**
- ✅ Nur EIN Glossar (keine Redundanz)
- ✅ Hyperlinks im Text
- ✅ Keine separate Akronym-Seite
- ✅ Saubere, professionelle PDF
- ✅ Alle Akronyme und Fachwörter an einer Stelle

---

Möchtest du, dass ich die Umstellung in deinen Kapiteln durchführe?

