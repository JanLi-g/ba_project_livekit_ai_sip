# Evaluations-Durchführungs-Checkliste

## PRE-EVALUATION SETUP

### Hardware & Software Check
- [ ] Docker Engine läuft und ist aktuell (v27.0+)
- [ ] Docker Compose läuft (v2.20+)
- [ ] Python 3.11+ installiert
- [ ] Pandas, NumPy, SciPy installiert: `pip install pandas numpy scipy`
- [ ] LiveKit Server & SIP Bridge Container starten: `docker-compose up -d`
- [ ] Agent Worker läuft: `docker logs agent-worker` zeigt keine Fehler
- [ ] Redis erreichbar: `docker exec redis redis-cli ping` → PONG

### Netzwerk & Zeitsynchronisation
- [ ] NTP läuft und synchronisiert: `w32tm /query /status` (Windows)
- [ ] Netzwerk-Latenz < 1ms zum Docker-Host (Ping-Test)
- [ ] Firewall: Ports 5060 (SIP), 5061 (UDP), 50000–50100 (RTP) freigegeben
- [ ] Smartphone mit Mobilfunk erreichbar (für SIP-Tests)
- [ ] OpenAI API-Key konfiguriert und getestet

### Datenverzeichnis
- [ ] Verzeichnis `evaluation/results/` existiert
- [ ] Verzeichnis `evaluation/logs/` existiert
- [ ] `TEST_PROTOCOL_TEMPLATE.md` liegt vor
- [ ] `analyze_results.py` ist ausführbar

### Monitoring-Tools bereit
- [ ] Terminal 1: `docker logs livekit-sip -f` (für SIP-Logs)
- [ ] Terminal 2: `docker logs agent-worker -f` (für Agent-Logs)
- [ ] Terminal 3: `docker stats --no-stream` vorbereitet
- [ ] Browser mit Web-UI öffnen: http://localhost:3000

---

## TESTFALL 1: WEB-UI BASELINE (N=30)

### Vorbereitung
- [ ] Browser-Tab öffnen: http://localhost:3000
- [ ] Kopfhörer/Lautsprecher angeschlossen und laut genug
- [ ] Mikrofon funktioniert (Test-Audio aufnehmen)
- [ ] Prompts vorbereitetet (kurz/mittel/lang)
- [ ] Protokoll-CSV öffnen und Header befüllen

### Durchführung: Kurz-Prompts (10 Calls)
**Zeit einplanen: ~15 Minuten**

```
For i in 1..10:
  1. Web-UI öffnen (Refresh falls nötig)
  2. [Prompt sprechen]: "Wie ist das aktuelle Wetter?"
  3. Agent-Antwort abhören, vollständig warten
  4. Sofort nach End: MOS bewerten (1-5) + Artefakte notieren
  5. Logs sammeln:
     - docker logs agent-worker --tail 50 > logs/webui_call_00X.log
     - docker stats --no-stream > logs/stats_call_00X.txt
  6. 30 Sekunden Pause (Agent recovered)
```

**Pro Call festhalten:**
- [ ] Exact Start-Time (HH:MM:SS.mmm)
- [ ] Exact End-Time (HH:MM:SS.mmm)
- [ ] MOS-Bewertung (1-5)
- [ ] Audioartefakte (ja/nein + Typ)
- [ ] CPU/RAM Peak (aus logs)

### Durchführung: Mittel-Prompts (15 Calls)
**Zeit einplanen: ~25 Minuten**

```
Prompt-Beispiele:
- "Erkläre mir die Funktionsweise eines Sprachmodells in 30 Sekunden."
- "Was sind die Vorteile und Nachteile von Cloud-Computing?"
- "Wie funktioniert eine SIP-Bridge in der Telefonie?"

[Analog zu Kurz-Prompts, aber 15x]
```

### Durchführung: Lang-Prompts (5 Calls)
**Zeit einplanen: ~10 Minuten**

```
Prompt-Beispiele:
- "Fasse die Architektur eines modernen Voice-Agent Systems zusammen, 
  inklusive Komponenten, Datenflusss und Herausforderungen."

[Analog zu Kurz-Prompts, aber 5x]
```

### Data Export nach Web-UI Tests
```powershell
# Alle Logs in einem Ordner sammeln
mkdir evaluation/results/webui_calls
cp logs/agent_worker.log evaluation/results/webui_calls/

# Docker-Stats sammeln
docker stats --no-stream > evaluation/results/docker_stats_webui.txt

# LiveKit Admin-API abrufen (pro Call)
for i in 1..30:
    curl -X GET "http://localhost:8080/twirp/livekit.RoomService/ListRooms" \
         -H "Authorization: Bearer <token>" \
         > evaluation/results/livekit_room_$i.json
```

---

## TESTFALL 2: SIP-INTEGRATION (N=10)

### Vorbereitung
- [ ] Smartphone bereit (Mobilfunk-Verbindung)
- [ ] DID +49XXXXXXX hat genug Guthaben / ist aktiv
- [ ] SIP-Bridge läuft: `docker logs livekit-sip` → keine Fehler
- [ ] Asterisk optional aktiv: `docker logs asterisk`
- [ ] Terminal mit SIP-Logs offen: `docker logs livekit-sip -f > logs/sip_calls_raw.log &`

### Durchführung: Anruf 1–10
**Zeit einplanen: ~20 Minuten**

```
For i in 1..10:
  1. Terminal 1: Zeit notieren (HH:MM:SS)
  2. Smartphone: +49XXXXXXX anwählen
  3. [Prompt sprechen, z.B.]: "Wie ist das Wetter?"
  4. Agent-Antwort abhören (oder feststellen, dass keine kommt)
  5. Anruf beenden (BYE)
  6. Sofort nach Call: MOS bewerten (falls Audio hörbar)
  7. 20 Sekunden warten (SIP-Cleanup)
```

**Pro Call Notieren:**
- [ ] Call-Start: HH:MM:SS
- [ ] INVITE empfangen? JA/NEIN
- [ ] Room erstellt? JA/NEIN
- [ ] Agent verbunden? JA/NEIN
- [ ] Audio hörbar? JA/NEIN
- [ ] Wenn JA: MOS (1-5)
- [ ] Audioartefakte? JA/NEIN + Typ
- [ ] Besonderheiten / Fehler?

**Beispiel Protokoll-Zeile:**
```
Call-001 | 14:23:45 | INVITE:✓ | Room:✓ | Agent:✓ | Audio:✓ | MOS:5 | Artefakte:✗ | Notes:-
Call-002 | 14:24:12 | INVITE:✓ | Room:✓ | Agent:✓ | Audio:✓ | MOS:4 | Artefakte:✗ | Notes:-
Call-003 | 14:24:38 | INVITE:✓ | Room:✓ | Agent:✓ | Audio:✗ | MOS:- | Artefakte:✓ | Notes:RTP Timeout
...
```

### Data Export nach SIP Tests
```powershell
# SIP-Logs finalisieren
pkill -f "docker logs livekit-sip"

# Agent-Worker-Logs für SIP sammeln
cp logs/agent_worker.log evaluation/results/agent_worker_sip.log

# LiveKit Admin-API für jeden Room abrufen
# (Falls dokumentiert in Logs)
```

---

## TESTFALL 3: LASTTESTS (optional, wenn Zeit)

### Vorbereitung
- [ ] Browser mit 3 Tabs vorbereiten (oder 3 Browser-Fenster)
- [ ] Jeder Tab: http://localhost:3000
- [ ] Terminal mit Load-Monitoring offen: `watch -n 1 'docker stats --no-stream'`
- [ ] Mittel-Prompt vorbereitet (identisch für alle 3 Calls)

### Durchführung: 1 Call Baseline (5x)
**Zeit einplanen: ~10 Minuten**

```
For run in 1..5:
  T0 = now()
  1. [Prompt sprechen in Tab 1]: "Erkläre SIP-Bridging."
  2. Warten auf Agent-Antwort
  3. Latenz notieren, CPU/RAM Peak notieren
  4. 60 Sekunden warten (Recovery)
```

**Tabelle:**
| Run | CPU (%) | RAM (MB) | Latenz (ms) | Erfolg |
|-----|---------|----------|------------|--------|
| 1   | XX      | XXXX     | XXXX       | ✓/✗    |
| 2   | XX      | XXXX     | XXXX       | ✓/✗    |
| ... |         |          |            |        |

### Durchführung: 2 Calls parallel (5x)
**Zeit einplanen: ~15 Minuten**

```
For run in 1..5:
  T0 = now()
  1. Tab 1 + Tab 2: Prompt GLEICHZEITIG sprechen (< 1s Versatz)
  2. Docker-Stats beobachten → CPU sollte ~60% gehen
  3. Warten auf BEIDE Agent-Antworten
  4. Latenzen + CPU/RAM notieren
  5. Fehler-Count notieren (z.B. Rate Limits)
  6. 60 Sekunden warten
```

### Durchführung: 3 Calls parallel (5x)
**Zeit einplanen: ~15 Minuten**

```
[Analog zu 2 Calls, aber alle 3 Tabs]
- Erwartet: CPU ~86%, Rate-Limit-Fehler möglich
- Falls 3x Fehler → Abbruch und Notieren
```

### Data Export nach Lasttests
```powershell
# Docker-Stats finalisieren
docker stats --no-stream > evaluation/results/docker_stats_loadtest.txt

# Aggregierte Metriken (Python-Skript):
python evaluation/analyze_results.py --load-test --export
```

---

## POST-EVALUATION

### Datenbereinigung & Validierung
- [ ] Alle `.log` Dateien in `evaluation/results/` kopiert
- [ ] Alle CSV/JSON in `evaluation/results/` vorhanden
- [ ] Timestamps auf Konsistenz überprüft (±100ms Abweichung ok)
- [ ] Keine Duplikate oder korrupten Dateien

### Python-Analyse ausführen
```bash
cd evaluation/

# Daten laden und analysieren
python analyze_results.py

# Outputs überprüfen:
# - latency_analysis.json
# - mos_analysis.json
# - sip_analysis.json
# - cpu_scaling.json
# - SUMMARY_REPORT.md
```

### Hypothesen-Status prüfen
- [ ] H1 (Latenz): 1000 ms ± 200 ms? → ✓ Bestätigt
- [ ] H2 (Audio-Qualität): 96% MOS ≥ 4? → ✓ Bestätigt
- [ ] H3 (SIP): INVITE/Room/Agent 100%, Audio ≥ 80%? → ✓/⭕ Bestätigt/Teils
- [ ] H4 (Skalierung): Bis 3 Calls stabil? → ✓ Bestätigt
- [ ] H5 (Kosten): $0.05 pro 5min? → ⭕ Wahrscheinlich

### Fehlerfälle dokumentieren
- [ ] SIP-Audio-Ausfallfall: Ursache im Log identifizieren?
- [ ] Rate-Limits bei 3 Calls: OpenAI-Tier erhöhen?
- [ ] Crashes/Timeouts: Stack-Trace in Logs?

### Final Report vorbereiten
- [ ] `SUMMARY_REPORT.md` überprüfen
- [ ] Screenshots/Logs für problematische Calls sammeln
- [ ] Tabellen für LaTeX-Bericht vorbereiten (kopieren aus JSON)

---

## NOTFALLPLAN

### Fehler: Agent-Worker nicht erreichbar
```bash
# Container neu starten
docker-compose restart agent-worker

# Logs überprüfen
docker logs agent-worker

# Ggf. OpenAI-Key prüfen
echo $OPENAI_API_KEY
```

### Fehler: LiveKit SIP-Bridge crasht
```bash
# Logs ansehen
docker logs livekit-sip

# Container neu starten
docker-compose restart livekit-sip

# Asterisk/SIP-Config überprüfen
docker exec asterisk asterisk -rx "pjsip show contacts"
```

### Fehler: Rate Limits erreicht
```bash
# Warte 60 Sekunden und wiederhole Test
# Oder: OpenAI API-Tier upgraden

# Temporär: Delays in Agent-Code erhöhen
# evaluation/delay_retry.py anpassen und neu deployen
```

### Fehler: Netzwerk-Probleme
```bash
# Latenz testen
ping -c 5 localhost

# Docker-Netzwerk überprüfen
docker network ls
docker network inspect untitled_default

# Ports überprüfen
netstat -an | grep 5060
netstat -an | grep 50000
```

---

## TIMELINE BEISPIEL

```
Montag 10:00–11:30:   Web-UI Kurz-Prompts (10 Calls)
Montag 11:30–12:00:   Pause
Montag 12:00–12:45:   Web-UI Mittel-Prompts (15 Calls)
Montag 12:45–13:00:   Mittagspause
Montag 13:00–13:15:   Web-UI Lang-Prompts (5 Calls)
Montag 13:15–13:45:   Data Export Web-UI

Dienstag 14:00–14:40: SIP-Integration Smartphone (10 Calls)
Dienstag 14:40–15:00: Data Export SIP

Mittwoch 10:00–11:00: Lasttests (1 Call: 5x)
Mittwoch 11:00–12:00: Lasttests (2 Calls: 5x)
Mittwoch 12:00–13:00: Lasttests (3 Calls: 5x)
Mittwoch 13:00–14:00: Analyse & Report

Donnerstag:            Buffer-Tag für Nachholungen
```

---

## TIPPS & TRICKS

1. **Batch-Processing**: Nutze Schleifen im Terminal, um 30 Calls automatisiert durchzuführen
2. **Parallel Logging**: Starte mehrere `docker logs` in separaten Terminals
3. **Backup Latenzen**: Falls ein Call fehlschlägt, log direkt vor/nach-Zeitstempel notieren
4. **Voice Recording**: Optional: Smartphone-Calls aufzeichnen (für späteren Review)
5. **API-Kosten Tracking**: Laufende Kosten im OpenAI Dashboard überprüfen

---

✅ **Checkliste komplett? → Los geht's mit den Tests!**

Good Luck! 🚀

