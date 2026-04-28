# 🚀 QUICK START – Tests durchführen & Daten sammeln

## Hardware Check ✅
```
Prozessor:   Intel Core i9-9900K @ 3.60 GHz (8C/16T)  ✓
RAM:         16 GB DDR4                               ✓
GPU:         NVIDIA GTX 1080 Ti (11 GB)              ✓
Monitor:     2560×1440 @ 144 Hz                       ✓
OS:          Windows 11 Pro (Build 26100)            ✓
```

---

## Phase 1: Web-UI Baseline (30 Calls)

### 1️⃣ Setup (5 Minuten)
```bash
# Terminal 1: Docker starten
cd E:\WebstormProjects\untitled
docker-compose up -d

# Terminal 1: Prüfen
docker ps
# → 5 Container sollten "Up" sein

# Terminal 2: Agent-Logs
docker logs agent-worker -f > logs/agent_raw.log &

# Terminal 3: Browser
# → Öffne http://localhost:3000
```

### 2️⃣ Kurz-Prompts (10x) – ~15 Minuten
```bash
# PowerShell Loop
for ($i = 1; $i -le 10; $i++) {
    Write-Host "=== Call $($i.ToString().PadLeft(2,'0')) (KURZ) ===" -ForegroundColor Green
    Read-Host "Drücke ENTER wenn Call bereit ist"
    
    # Browser: http://localhost:3000
    # [Sprechen]: "Wie ist das aktuelle Wetter?"
    # → Agent-Antwort abhören
    
    # MOS bewerten (1-5)
    $mos = Read-Host "MOS (1-5)"
    
    # Artefakte?
    $artifacts = Read-Host "Artefakte (keine/rauschen/delay/dropout)"
    
    # CSV-Zeile speichern
    # Format: call_001,short,"Prompt",start_time,latency,mos,artifacts,...
    
    Start-Sleep -Seconds 30
}
```

**Prompts (wiederholt für Calls 1–10):**
- "Wie ist das aktuelle Wetter?"

### 3️⃣ Mittel-Prompts (15x) – ~25 Minuten
```bash
# Prompts (beliebig auf 15 Calls verteilt):
Prompts = [
    "Erkläre mir die Funktionsweise eines Sprachmodells in 30 Sekunden.",
    "Was sind die Vorteile und Nachteile von Cloud-Computing?",
    "Wie funktioniert eine SIP-Bridge in der Telefonie?",
    "Beschreibe den Unterschied zwischen WebRTC und SIP.",
    "Was ist eine Voice Activity Detection und warum ist sie wichtig?"
]

# [Loop: 15 Calls mit Prompts aus Liste (zyklisch)]
```

### 4️⃣ Lang-Prompts (5x) – ~10 Minuten
```bash
# Prompts:
Lang_Prompts = [
    "Fasse die Architektur eines modernen Voice-Agent Systems zusammen, 
     inklusive Komponenten, Datenfluss und Herausforderungen.",
    "Erläutere die Challenges bei der Integration von LLMs in 
     SIP-basierte Telefonsysteme unter Berücksichtigung von 
     Latenz, Skalierung und Datenschutz."
]

# [Loop: 5 Calls]
```

### 5️⃣ Daten Export (10 Minuten)
```bash
# 1. Logs sammeln
mkdir -p evaluation/results/webui_calls
cp logs/call_*.log evaluation/results/webui_calls/

# 2. CSV mit Messungen erstellen
# (Manuell aus Notizen oder via Skript)

# 3. Python-Analyse
python evaluation/analyze_results.py --webui

# 4. Outputs überprüfen
ls evaluation/results/
# → webui_calls.csv
# → latency_analysis.json
# → mos_analysis.json
```

---

## Phase 2: SIP-Smartphone (10 Calls)

### 1️⃣ Setup (5 Minuten)
```bash
# Terminal mit SIP-Logs
docker logs livekit-sip -f > logs/sip_raw.log &

# Prüfen: SIP-Bridge läuft
docker logs livekit-sip | tail -20
# → "listening on :5060/udp"

# Smartphone: Mobilfunk aktiviert
# → SMS senden zu Plusnet-Testnum: "Test SIP" (falls nötig)
```

### 2️⃣ 10 Smartphone-Anrufe (30 Minuten)
```bash
# For Call 1-10:

1. Zeitstempel notieren: HH:MM:SS
2. Smartphone: +49XXXXXXX wählen
3. Warten auf Ansage: "Willkommen bei Voice-Agent"
4. Prompt sprechen:
   - Calls 1–5: Kurz-Prompts
   - Calls 6–10: Mittel-Prompts
5. Agent-Antwort abhören
6. Dokumentieren:
   ✓ INVITE empfangen? (Ja/Nein)
   ✓ Room erstellt? (Ja/Nein)
   ✓ Agent verbunden? (Ja/Nein)
   ✓ Audio hörbar? (Ja/Nein)
   ✓ MOS wenn hörbar: 1–5
   ✓ Artefakte? (keine / Rauschen / Delay / Dropout)
7. Anruf beenden
8. 30 Sekunden warten
```

### 3️⃣ Daten Export (10 Minuten)
```bash
# 1. Logs finalisieren
pkill -f "docker logs livekit-sip"

# 2. SIP-Logs isolieren
cp logs/sip_raw.log evaluation/results/

# 3. CSV mit SIP-Messdaten erstellen
# (Manuell aus Notizen)

# 4. Python-Analyse
python evaluation/analyze_results.py --sip

# 5. Outputs überprüfen
ls evaluation/results/
# → sip_calls.csv
# → sip_integration_analysis.json
```

---

## Phase 3: (Optional) Lasttests

### 1 Call Baseline (5x)
```bash
# For run 1-5:

1. Browser Tab 1: http://localhost:3000
2. Sprechen: "Erkläre SIP-Bridging."
3. Messung: CPU Peak, RAM, Latenz, Erfolg?
4. Warte 60 Sekunden
```

### 2 Calls Parallel (5x)
```bash
# For run 1-5:

1. Browser Tab 1 + Tab 2: http://localhost:3000
2. GLEICHZEITIG sprechen (< 1s Versatz):
   - Tab 1: "Erkläre SIP-Bridging."
   - Tab 2: "Erkläre SIP-Bridging."
3. Messung: CPU Peak, RAM, beide erfolgreich?
4. Fehler? (Rate Limit, Timeout?)
5. Warte 60 Sekunden
```

### 3 Calls Parallel (5x)
```bash
# [Identisch zu 2 Calls, aber Tab 1+2+3]
# Erwartet: CPU 85%+, möglich Rate Limit Fehler
```

---

## 📊 Daten Eintragen

### Automatisch via Skript (empfohlen):
```bash
# Terminal öffnen
python evaluation/data_collector.py webui

# → Skript führt dich interaktiv durch
# → Automatisch CSV erstellt
# → Eingabefelder für: call_id, category, mos, artifacts, cpu, ram, notes
```

### Manuell via CSV:
```bash
# 1. CSV öffnen: evaluation/results/webui_calls.csv
# 2. Für jeden Call eine Zeile hinzufügen:

call_id,category,prompt,start_time,e2e_latency_ms,mos,artifacts,...
001,short,"Wie ist das Wetter?",2025-12-28T10:00:00,920,5,none,...
002,short,"Wie ist das Wetter?",2025-12-28T10:00:45,950,5,none,...
...
```

---

## 📈 Analyse durchführen

```bash
# 1. Python-Skript ausführen
python evaluation/analyze_results.py

# 2. Outputs überprüfen
ls -la evaluation/results/
# → webui_calls.csv
# → sip_calls.csv
# → latency_analysis.json
# → mos_analysis.json
# → cpu_scaling_analysis.json
# → SUMMARY_REPORT.md

# 3. SUMMARY_REPORT anschauen
cat evaluation/results/SUMMARY_REPORT.md
```

---

## 📝 Ergebnisse in Kapitel 6 eintragen

### Web-UI Tabellen (aus JSON):
```latex
% Aus latency_analysis.json:
Mittelwert (μ):    XXX ms
Median:            XXX ms
Standardabw. (σ): XXX ms
Min/Max:           XXX/XXX ms

% Aus mos_analysis.json:
Exzellent (5):     XX/30 (XX%)
Gut (4):           XX/30 (XX%)
Akzeptabel (3):    XX/30 (XX%)
```

### SIP Tabellen (aus JSON):
```latex
% Aus sip_integration_analysis.json:
INVITE empfangen:  10/10 (100%)
Room erstellt:     10/10 (100%)
Agent verbunden:   10/10 (100%)
Audio hörbar:      X/10 (XX%)
```

### CPU-Skalierung (aus JSON):
```latex
% Aus cpu_scaling_analysis.json:
1 Call:   XX% CPU, linear model: CPU = 7% + 26% × N
2 Calls:  XX% CPU, R² = 0.99X
3 Calls:  XX% CPU
```

---

## 🎯 Zeitplanung

```
Montag 10:00–11:30:   Web-UI Kurz (10 Calls)
Montag 11:30–12:00:   Break
Montag 12:00–12:45:   Web-UI Mittel (15 Calls)
Montag 12:45–13:15:   Mittagspause
Montag 13:15–13:30:   Web-UI Lang (5 Calls)
Montag 13:30–14:00:   Data Export & Analyse

Dienstag 14:00–14:40: SIP Smartphone (10 Calls)
Dienstag 14:40–15:15: Data Export & Analyse

[Optional]
Mittwoch 10:00–11:00: Lasttests (1 Call, 5x)
Mittwoch 11:00–12:00: Lasttests (2 Calls, 5x)
Mittwoch 12:00–13:00: Lasttests (3 Calls, 5x)

Donnerstag 10:00–11:00: Daten validieren & finalisieren
Donnerstag 11:00–12:00: Kapitel 6 mit Ergebnissen füllen
```

---

## ✅ Checkliste

### Vor Tests
- [ ] Docker läuft: `docker ps` → 5 Container Up
- [ ] OpenAI API funktioniert (Test-Request)
- [ ] Web-UI erreichbar: http://localhost:3000
- [ ] Smartphone mit Mobilfunk verbunden
- [ ] evaluation/results/ Verzeichnis leer
- [ ] Python-Skripte getestet
- [ ] Genug Speicherplatz (> 5 GB)

### Während Tests
- [ ] Terminals laufen: Agent-Logs + SIP-Logs + Monitoring
- [ ] Jeder Call dokumentiert (MOS, Artefakte, CPU/RAM)
- [ ] CSV regelmäßig gespeichert
- [ ] Fehler fotografiert/notiert

### Nach Tests
- [ ] Alle Logs gesammelt
- [ ] CSV finalisiert
- [ ] Python-Analyse erfolgreich
- [ ] JSON/Statistiken überprüft
- [ ] Ergebnisse in Kapitel 6 eingetragen

---

## 🚀 READY TO GO!

**Start mit:**
```bash
cd E:\WebstormProjects\untitled
docker-compose up -d
# → Browser: http://localhost:3000
# → Python: python evaluation/data_collector.py webui
```

**Viel Erfolg! 🎓**


