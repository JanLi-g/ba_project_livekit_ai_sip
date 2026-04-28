# 📊 Evaluation Guide - KI-Sprach-Assistent Bachelorarbeit

## 🎯 Ziel

Objektive, statistisch fundierte Bewertung des Voice-Agent-Systems anhand von:
- ✅ **Performance:** End-to-End Latenz < 2000ms
- ✅ **Zuverlässigkeit:** Erfolgsrate > 90%
- ✅ **Ressourceneffizienz:** CPU < 1%, RAM < 100MB
- ✅ **Komponentenanalyse:** LLM als Engpass identifizieren
- ✅ **SIP-Integration:** Asterisk Performance

---

## 📋 Dateistruktur

```
analysis/
├── raw/
│   ├── docker_stats.csv          # Ressourcen-Metriken (auto. gesammelt)
│   ├── events.csv                # Agent Timing-Logs (auto. gesammelt)
│   └── (werden bei Analyse gefüllt)
├── processed/
│   ├── latency_summary.csv       # Latenz-Statistiken
│   ├── resource_summary.csv      # Ressourcen-Statistiken
│   ├── hypothesis_results.csv    # Hypothesen-Verifikation
│   ├── latency_boxplot.png       # Visualisierung
│   ├── resource_timeline.png     # Visualisierung
│   ├── latency_table.tex         # Kopierbar für Thesis!
│   └── resource_table.tex        # Kopierbar für Thesis!
├── run_evaluation.py             # Analyse-Skript (Hauptdatei)
├── EVALUATION_PLAN.md            # Detaillierter Plan
└── requirements-analysis.txt     # Dependencies (pandas, scipy, matplotlib)

python/
├── agent_worker_evaluation.py    # Agent mit Timing-Logging
└── (weitere Worker-Varianten)

powershell/
├── measure-resources.ps1         # Docker Stats Collector
└── (weitere Test-Skripte)

thesis/
├── 06_evaluation.tex             # Aktuelles Evaluationskapitel
├── 06_evaluation_template.tex    # Template mit Platzhaltern
└── (weitere Kapitel)

root/
└── run-evaluation.bat            # Schnellstart-Skript für Windows
```

---

## 🚀 Quick Start

### Schritt 1: Vorbereitung (einmalig)

```powershell
# Wechsle ins Projektverzeichnis
cd E:\WebstormProjects\untitled

# Installiere Python-Dependencies
pip install pandas matplotlib scipy numpy requests

# Prüfe Docker
docker-compose ps
```

### Schritt 2: Automatische Evaluation durchführen

```powershell
# Option A: Windows Batch-Skript (einfachster Weg!)
run-evaluation.bat

# Option B: Manuell in PowerShell
# (siehe Abschnitt "Manuelle Durchführung" unten)
```

### Schritt 3: Ergebnisse in Thesis integrieren

```powershell
# 1. Öffne generierte CSV-Datei
notepad analysis/processed/latency_summary.csv

# 2. Öffne Thesis-Template
code thesis/06_evaluation_template.tex

# 3. Ersetze [Placeholder] mit Werten
# 4. Kopiere LaTeX-Tabellen aus:
#    - analysis/processed/latency_table.tex
#    - analysis/processed/resource_table.tex

# 5. Integriere PNG-Grafiken:
#    - analysis/processed/latency_boxplot.png
#    - analysis/processed/resource_timeline.png
```

---

## 📖 Detaillierte Durchführung

### Phase 1: Setup (vor Test-Calls)

**Dauer:** ~15 Minuten

```bash
# 1. Docker-Container prüfen/starten
docker-compose up -d

# Verifiziere: alle 4 Container sollten laufen
docker-compose ps
# => livekit, livekit-sip, asterisk, redis (alle "running")

# 2. Agent Worker starten (neues Terminal)
cd python
python agent_worker_evaluation.py
# => Sollte "✅ Prewarm abgeschlossen" zeigen

# 3. Docker Stats Collector starten (3. Terminal)
cd powershell
./measure-resources.ps1 -DurationMinutes 30
# => Sollte "Starte Messung..." zeigen
# => Läuft im Hintergrund, bis Phase 3 abgeschlossen
```

**Troubleshooting:**
- `docker-compose up -d` fehlgeschlagen? → Prüfe Docker Desktop Installation
- Agent Worker startet nicht? → Prüfe `.env.local` für API-Keys
- Measure-resources.ps1 funktioniert nicht? → Prüfe PowerShell Execution Policy

### Phase 2: Test-Calls durchführen (~45 Minuten)

**N=30 Web-Calls:**

```
1. Browser öffnen: http://localhost:3000
2. "Voice Agent" wählen / "Start Call" klicken
3. Mikrofon erlauben (Browser-Permission)
4. Prompt sprechen (s. unten)
5. Agent-Antwort abwarten
6. Logs automatisch in events.csv geschrieben
7. Repeat 30x total
```

**Test-Prompts (standardisiert, um Reproduzierbarkeit zu erhöhen):**

| Kategorie | Text | N | Dauer |
|-----------|------|---|-------|
| **KURZ** | "Wie geht es dir?" | 5 | 3-5s |
| **KURZ** | "Wer bist du?" | 5 | 3-5s |
| **MITTEL** | "Erkläre Containerisierung in einem Satz." | 8 | 8-12s |
| **MITTEL** | "Wie funktioniert ein SIP-Anruf?" | 7 | 8-12s |
| **LANG** | "Beschreibe die Vor- und Nachteile von Cloud-basierten LLMs für Telefonie-Systeme." | 5 | 15-20s |

**N=10 SIP-Calls (optional, wenn Asterisk konfiguriert):**

```
1. SIP-Client verwenden (z.B. X-Lite, Linphone)
2. Konfiguriere SIP-Account zu Asterisk (localhost:5060)
3. Rufe auf (z.B. Extension "2001")
4. Spreche Prompt
5. Warte auf Agent-Antwort
6. Repeat 10x
```

**Monitoring während Phase 2:**

- Terminal 1: Agent Worker → Sollte "✅ METRIC: greeting_sent" zeigen
- Terminal 2: measure-resources.ps1 → Sollte "[NN%] timestamp - Container erfasst" zeigen
- Browser Console: Keine kritischen Fehler (F12 → Console)

### Phase 3: Analyse durchführen (~10 Minuten)

**Nach allen Test-Calls:**

```powershell
# 1. Agent Worker & Docker Stats beenden (Strg+C in jedem Terminal)
# 2. Ausgangsverzeichnis:
cd E:\WebstormProjects\untitled

# 3. Analyse ausführen
python analysis/run_evaluation.py

# Erwartete Ausgabe:
# ✅ Ressourcen-Analyse
# ✅ Hypothesen-Verifikation
# 💾 Dateien in analysis/processed/ generiert
```

**Generierte Dateien prüfen:**

```powershell
ls analysis/processed/

# Sollte folgende Dateien enthalten:
# - latency_summary.csv
# - resource_summary.csv
# - hypothesis_results.csv
# - latency_boxplot.png
# - resource_timeline.png
# - latency_table.tex
# - resource_table.tex
```

---

## 📊 Interpreting Results

### CSV-Dateien

**latency_summary.csv (Beispiel):**
```
event_type,N,Mean,Median,Std,Min,Max,P95
stt_request,30,450.5,420.0,125.3,280,650,580
llm_request,30,1200.0,1150.0,300.0,800,1800,1650
tts_request,30,320.0,300.0,80.0,150,500,450
room_connected,30,150.0,140.0,40.0,80,250,200
greeting_sent,30,1850.0,1800.0,400.0,1200,2500,2300
```

**Interpretation:**
- STT (Whisper): ~450ms durchschnittlich ✅
- LLM (GPT-4o-mini): ~1200ms durchschnittlich (Engpass!) ⚠️
- TTS (OpenAI): ~320ms durchschnittlich ✅
- E2E (greeting_sent): ~1850ms < 2000ms → **H1 BESTANDEN** ✅

**resource_summary.csv (Beispiel):**
```
container_name,CPU_Mean,CPU_Max,CPU_Std,RAM_Mean_MB,RAM_Max_MB,RAM_Std_MB
untitled-asterisk-1,0.42,0.61,0.06,66.64,66.65,0.01
untitled-livekit-1,0.1,0.18,0.06,14.44,15.06,0.23
untitled-livekit-sip-1,0.04,0.06,0.01,11.8,12.14,0.2
untitled-redis-1,0.32,0.34,0.01,3.78,3.84,0.11
```

**Interpretation:**
- CPU-Auslastung: alle < 1% ✅
- RAM: alle < 100MB ✅
- → **H3 & H5 BESTANDEN** ✅

---

## 📈 Hypothesen-Checkliste

Nach Analyse: Markiere die Ergebnisse

```
☐ H1 (E2E < 2000ms): BESTANDEN / NICHT BESTANDEN
   Mean E2E: _____ ms

☐ H2 (Success > 90%): BESTANDEN / NICHT BESTANDEN
   Success Rate: _____ %

☐ H3 (Ressourcen): BESTANDEN / NICHT BESTANDEN
   CPU Mean: _____ %, RAM Max: _____ MB

☐ H4 (LLM > STT, p<0.05): BESTANDEN / NICHT BESTANDEN
   p-value: _____, Cohen's d: _____

☐ H5 (Asterisk OK): BESTANDEN / NICHT BESTANDEN
   Asterisk CPU: _____ %, RAM: _____ MB
```

---

## 📝 Integration in Thesis (06_evaluation.tex)

### Template verwenden

```bash
# 1. Öffne Template
code thesis/06_evaluation_template.tex

# 2. Ersetze [Placeholder] mit Werten aus CSV:
#    [Mean] → aus latency_summary.csv
#    [Median] → aus latency_summary.csv
#    etc.

# 3. Kopiere LaTeX-Tabellen:
#    a) Öffne analysis/processed/latency_table.tex
#    b) Copy-Paste in dein Thesis-Kapitel
#    c) Wiederhole mit resource_table.tex

# 4. Integriere PNG-Grafiken:
\includegraphics[width=0.9\textwidth]{../analysis/processed/latency_boxplot.png}
\includegraphics[width=0.9\textwidth]{../analysis/processed/resource_timeline.png}

# 5. Speichern & Kompilieren
pdflatex main.tex
```

---

## 🔍 Troubleshooting

### Problem: Keine events.csv erzeugt
**Lösung:**
- Agent Worker läuft? → Prüfe Terminal auf Fehler
- .env.local vorhanden? → Prüfe API-Keys (OPENAI_API_KEY)
- Test-Calls durchgeführt? → Sonst keine Events zum Loggen

### Problem: Docker Stats leer
**Lösung:**
- `docker-compose ps` → Alle Container running?
- Docker auf Windows? → Ggf. Docker Desktop neustarten
- Powershell-Script berechtigung? → `Set-ExecutionPolicy -ExecutionPolicy Bypass`

### Problem: Analyse-Fehler (Python)
**Lösung:**
```powershell
# Dependencies neu installieren
pip install --upgrade pandas matplotlib scipy numpy requests

# Prüfe Python Version
python --version  # Sollte >= 3.9 sein
```

---

## 📞 Support

Bei Fragen:
1. Siehe `EVALUATION_PLAN.md` für detaillierte Dokumentation
2. Prüfe `analysis/run_evaluation.py` Kommentare
3. Kontaktiere Betreuer mit Screenshots der Fehler

---

## ✅ Checkliste für erfolgreiche Evaluation

- [ ] `.env.local` mit API-Keys konfiguriert
- [ ] Docker-Container starten & laufen
- [ ] Agent Worker startet fehlerfrei
- [ ] Browser-UI funktioniert (http://localhost:3000)
- [ ] 30+ Web-Calls durchgeführt
- [ ] 10+ SIP-Calls durchgeführt (optional)
- [ ] Docker Stats Collector ~30min gelaufen
- [ ] `analysis/run_evaluation.py` erfolgreich ausgeführt
- [ ] CSV-Dateien in `analysis/processed/` gefüllt
- [ ] PNG-Grafiken erzeugt
- [ ] Werte in Thesis-Template eingefügt
- [ ] Thesis kompiliert (LaTeX)
- [ ] PDF reviewt und freigegeben

---

**Status:** Ready for Evaluation  
**Letzte Aktualisierung:** 2025-12-12  
**Autor:** Evaluation Pipeline

