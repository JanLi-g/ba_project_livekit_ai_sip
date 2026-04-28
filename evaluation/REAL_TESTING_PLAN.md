# Real-World Testing Plan – Basierend auf echte Hardware

## 🖥️ Echte Hardware (validiert aus DxDiag)

```
Processor:     Intel Core i9-9900K @ 3.60 GHz (8 Cores, 16 Threads)
               → DEUTLICH schneller als vorher angenommener i5-10400F!
               → Docker-Overhead sollte minimal sein

RAM:           16 GB DDR4
               → Genug für alle Services + Buffer

GPU:           NVIDIA GeForce GTX 1080 Ti (11 GB VRAM)
               → Optional für lokale LLM-Tests später

Monitor:       2560×1440 @ 144 Hz
               → Gute Auflösung für Web-UI Tests

OS:            Windows 11 Pro 64-bit (Build 26100)
```

**Implikation für Tests:**
- ✅ Bessere CPU-Performance als erwartet
- ✅ Höhere Skalierbarkeit zu erwarten
- ✅ GPU könnte für zukünftige Optimierungen genutzt werden

---

## 📅 Test-Durchführungs-Plan

### Phase 1: Web-UI Baseline Tests (1,5 Tage)

**Ziel**: N=30 Calls mit exakten Messungen

#### Setup vor Tests
```bash
# 1. Alle Services starten
docker-compose up -d

# 2. Health Check
docker ps
docker logs livekit-sip | grep -E "(INFO|ERROR|listening)"
docker logs agent-worker | grep -E "(ready|listening)"

# 3. OpenAI API testen
curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"test"}]}'

# 4. Terminals vorbereiten
# Terminal 1: docker logs livekit-sip -f > logs/sip_raw.log
# Terminal 2: docker logs agent-worker -f > logs/agent_raw.log
# Terminal 3: Monitoring (watch -n 1 'docker stats')
```

#### Durchführung: Kurz-Prompts (10 Calls)
```bash
# Loop in PowerShell
for ($i = 1; $i -le 10; $i++) {
    Write-Host "=== Call $i (KURZ) ===" 
    $start = Get-Date
    
    # Browser öffnen: http://localhost:3000
    # [Prompt sprechen]: "Wie ist das aktuelle Wetter?"
    # Antwort abhören
    
    $end = Get-Date
    $latency = ($end - $start).TotalMilliseconds
    Write-Host "E2E Latency: $latency ms"
    
    # MOS notieren (1-5)
    # Logs speichern
    docker logs agent-worker --tail 20 > "logs/call_short_$('{0:00}' -f $i).log"
    
    Start-Sleep -Seconds 30  # Recovery
}
```

**Pro Call notieren in CSV:**
```
call_id,category,prompt,start_time,e2e_latency_ms,mos,artifacts,cpu_percent,ram_mb,notes
001,short,"Wie ist das Wetter?",2025-12-28T10:00:00,920,5,none,28,580,"clear audio"
002,short,"Wie ist das Wetter?",2025-12-28T10:00:45,950,5,none,30,590,"clear audio"
...
```

#### Durchführung: Mittel-Prompts (15 Calls)
```
Prompts:
- "Erkläre mir die Funktionsweise eines Sprachmodells in 30 Sekunden."
- "Was sind die Vorteile und Nachteile von Cloud-Computing?"
- "Wie funktioniert eine SIP-Bridge in der Telefonie?"
- "Beschreibe den Unterschied zwischen WebRTC und SIP."
- "Was ist eine Voice Activity Detection und warum ist sie wichtig?"

[Loop: 15 Calls mit identischem Prozess]
```

#### Durchführung: Lang-Prompts (5 Calls)
```
Prompts:
- "Fasse die Architektur eines modernen Voice-Agent Systems zusammen,
  inklusive Komponenten, Datenfluss und Herausforderungen."
- "Erläutere die Challenges bei der Integration von LLMs in 
  SIP-basierte Telefonsysteme unter Berücksichtigung von Latenz, 
  Skalierung und Datenschutz."

[Loop: 5 Calls mit identischem Prozess]
```

#### Data Export nach Web-UI Tests
```bash
# 1. Alle Logs sammeln
mkdir -p evaluation/results/webui_calls
cp logs/call_*.log evaluation/results/webui_calls/

# 2. CSV mit allen Measurements erstellen
# (aus aufgesammelten Daten)

# 3. Docker-Stats finalisieren
docker stats --no-stream > evaluation/results/docker_stats_webui.txt

# 4. JSON-Datei für Analyse
# Format: [{call_id, category, e2e_latency, mos, cpu, ram, ...}, ...]
```

---

### Phase 2: SIP-Integration (Smartphone-Anrufe) – 0,5 Tage

**WICHTIG: ECHTE Anrufe vom Smartphone, nicht Softphone!**

#### Vorbereitung
```bash
# 1. SIP-Bridge vorbereitet
docker logs livekit-sip -f > logs/sip_calls_raw.log &

# 2. Plusnet-Trunk aktiv
# → DID +49XXXXXXX hat Guthaben?
# → Ist registriert bei LiveKit?

# 3. Terminal mit docker logs offenlassen
```

#### Durchführung: 10 Smartphone-Anrufe
```bash
# For each call:

1. Zeitstempel notieren: HH:MM:SS.mmm
2. Smartphone: +49XXXXXXX anwählen
3. [Warten auf "Willkommen bei Voice-Agent"]
4. Prompt sprechen: [identisch zu Web-UI]
   - Call 1-5: Kurz-Prompts
   - Call 6-10: Mittel-Prompts
5. Agent-Antwort abhören
6. Qualität bewerten: Audio hörbar? MOS? Artefakte?
7. Anruf beenden
8. 30 Sekunden warten (Cleanup)

Dokumentieren:
- INVITE empfangen? JA/NEIN
- Room erstellt? JA/NEIN
- Agent verbunden? JA/NEIN
- Audio hörbar? JA/NEIN
- MOS (falls hörbar): 1–5
- Audioartefakte? [keine / Rauschen / Verzögerung / Dropout]
- Verdächtige Log-Einträge?
```

**CSV-Format:**
```
call_id,timestamp,prompt,invite_ok,room_ok,agent_ok,audio_ok,mos,artifacts,error_log_line
001,2025-12-28T14:00:00,"Wie ist das Wetter?",true,true,true,true,5,none,"-"
002,2025-12-28T14:00:45,"Wie ist das Wetter?",true,true,true,true,4,"short delay","[WARN] RTP late packets"
...
```

#### Data Export
```bash
# 1. SIP-Logs finalisieren
pkill -f "docker logs livekit-sip"

# 2. Agent-Logs für SIP isolieren
cp logs/agent_raw.log evaluation/results/agent_worker_sip.log

# 3. Asterisk Logs (falls nötig)
docker logs asterisk > evaluation/results/asterisk_sip.log

# 4. LiveKit Admin-API für Room-Sessions abrufen
```

---

### Phase 3: Lasttests (optional) – 1 Tag

**Nur wenn Zeit & Budget übrig**

```bash
# Test 1: Baseline (1 Call, 5x wiederholt)
for run in {1..5}; do
    echo "=== Load Test: 1 Call (Run $run) ==="
    # Browser Tab 1: Prompt sprechen
    # Messung: CPU, RAM, Latenz
    sleep 60  # Recovery
done

# Test 2: 2 Calls parallel (5x)
for run in {1..5}; do
    echo "=== Load Test: 2 Calls (Run $run) ==="
    # Browser Tab 1 + Tab 2: GLEICHZEITIG Prompts sprechen
    # Messung: CPU Peak, RAM, Fehler
    sleep 60
done

# Test 3: 3 Calls parallel (5x)
for run in {1..5}; do
    echo "=== Load Test: 3 Calls (Run $run) ==="
    # Browser Tab 1 + 2 + 3: GLEICHZEITIG
    # Erwartet: Rate Limits bei OpenAI API
    sleep 60
done
```

---

## 📊 Datensammlung & Analyse

### Nach jedem Testfall:

```bash
# 1. CSV-Dateien zusammenstellen
python3 << 'EOF'
import pandas as pd
import json

# Web-UI Daten laden
webui_data = pd.read_csv('evaluation/results/webui_calls.csv')

# SIP Daten laden
sip_data = pd.read_csv('evaluation/results/sip_calls.csv')

# Analyse durchführen
print(f"Web-UI Latenz: μ={webui_data['e2e_latency_ms'].mean():.0f} ms")
print(f"SIP Success Rate: {(sip_data['audio_ok'].sum()/len(sip_data)*100):.1f}%")

# JSON exportieren
with open('evaluation/results/summary_stats.json', 'w') as f:
    json.dump({
        'webui': webui_data.describe().to_dict(),
        'sip': sip_data.describe().to_dict()
    }, f, indent=2)
EOF

# 2. Python-Analyse starten
python evaluation/analyze_results.py

# 3. Outputs überprüfen
ls -la evaluation/results/
```

---

## 🎯 Erwartete Resultate (basierend auf besserer Hardware)

### Web-UI (mit i9-9900K statt i5):
- **Latenz**: Sollte BESSER sein (schneller CPU)
  - Prognose: 800–1100 ms statt 800–1450 ms
  - LLM-Latenz weniger beeinträchtigt durch CPU-Konkurrenz
  
- **CPU-Auslastung**: Sollte NIEDRIGER sein
  - Prognose: 20–25% pro Call statt 31%
  - Bis zu 4–5 Calls parallel möglich statt nur 3

- **Audio-Qualität**: Sollte GLEICH sein
  - Prognose: Immer noch 96% MOS ≥ 4
  - CPU-Last spielte keine Rolle bei MOS

### SIP (Smartphone):
- **Zuverlässigkeit**: Sollte BESSER sein
  - Prognose: 95%+ Audio hörbar statt 90%
  - Weniger transiente Fehler durch bessere CPU

### Lasttests:
- **Skalierung**: Sollte bis 4–5 Calls stabil sein
  - Prognose: CPU maximal ~90% bei 5 Calls
  - Rate Limit immer noch Bottleneck (aber nicht CPU)

---

## 📝 Dokumentation während Tests

### Terminal 1 (Agent Logs):
```
[Agent-Worker läuft und logt]
→ Speichern: logs/agent_raw.log
→ Nach Tests: evaluate auf Timestamps & Latenzen
```

### Terminal 2 (SIP Logs):
```
[SIP-Bridge läuft und logt]
→ Speichern: logs/sip_raw.log
→ Nach Tests: evaluate auf INVITE/Room/RTP-Fehler
```

### Terminal 3 (Monitoring):
```
docker stats --no-stream
→ Alle 5–10 Sekunden screenshot
→ CSV zusammenstellen
```

### Browser Developer Tools (optional):
```
F12 → Network Tab
→ WebSocket zu LiveKit monitoren
→ Audio-Packages zählen (für Bitrate-Validierung)
```

---

## ✅ Final Check vor Tests

- [ ] Docker-Compose läuft: `docker ps` zeigt 5 Container
- [ ] OpenAI API funktioniert: Test-Request erfolgreich
- [ ] Web-UI erreichbar: http://localhost:3000
- [ ] Smartphone mit Mobilfunk verbunden
- [ ] Terminals vorbereitet (3 Logs parallel)
- [ ] Evaluation-Verzeichnis leer/ready
- [ ] Python-Analyse-Skript getestet
- [ ] Speicherplatz > 10 GB verfügbar (für Logs)
- [ ] Internet-Verbindung stabil
- [ ] OpenAI Rate Limits überprüft (Tier 1: 500 RPM)

---

## 📋 Schätzung Gesamtdauer

```
Phase 1 (Web-UI):        1,5 Tage
  - Kurz (10x):          0,25 Tage
  - Mittel (15x):        0,4 Tage
  - Lang (5x):           0,15 Tage
  - Export & Cleanup:    0,7 Tage

Phase 2 (SIP):           0,5 Tage
  - 10 Anrufe:           0,3 Tage
  - Export & Cleanup:    0,2 Tage

Phase 3 (Lasttests):     1 Tag (optional)
  - 1 Call (5x):         0,25 Tage
  - 2 Calls (5x):        0,35 Tage
  - 3 Calls (5x):        0,4 Tage

Analyse & Report:        0,5 Tage

────────────────
TOTAL:           2,5–3,5 Tage (ohne Lasttests)
                 3,5–4,5 Tage (mit Lasttests)
```

---

## 🚀 Los geht's!

**Status: READY TO EXECUTE**

Startet Phase 1 wenn bereit → Daten sammeln → Analyse → In Evaluation-Kapitel eintragen


