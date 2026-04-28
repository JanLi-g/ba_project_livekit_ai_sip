# Evaluations-Testprotokoll

## Testfall 1: Web-UI Baseline Calls

### Call #001
**Datum/Uhrzeit**: 2025-12-XX, HH:MM:SS  
**Prompt-Kategorie**: [Kurz | Mittel | Lang]  
**Prompt-Text**: "..."

#### Objective Metrics
| Metrik | Wert | Einheit |
|--------|------|---------|
| Audio-Start | HH:MM:SS.mmm | Timestamp |
| STT-Ende | HH:MM:SS.mmm | Timestamp |
| LLM-Ende | HH:MM:SS.mmm | Timestamp |
| TTS-Ende | HH:MM:SS.mmm | Timestamp |
| Audio-Ende | HH:MM:SS.mmm | Timestamp |
| **End-to-End Latenz** | XXX | ms |
| Netzwerk-Latenz | XX | ms |
| Audio-Buffering | XX | ms |
| STT-Zeit | XX | ms |
| LLM-Zeit | XX | ms |
| TTS-Zeit | XX | ms |
| Jitter (RTP) | X | ms |
| Paketverlust | X.X | % |
| Bitrate (avg) | XX | kbps |

#### Subjektive Metriken (MOS)
| Kriterium | Bewertung (1-5) | Notizen |
|-----------|-----------------|--------|
| Verständlichkeit | X | [z.B. kristallklar / verständlich / leichte Verzerrungen] |
| Natürlichkeit (TTS) | X | [z.B. fließend / synthetisch / Artefakte] |
| Gesamteindruck | X | [z.B. exzellent / gut / akzeptabel] |

#### Audioartefakte (ja/nein)
- [ ] Rauschen
- [ ] Verzögerungen/Stutter
- [ ] Dropout/Abbruch
- [ ] Verzerrungen
- [ ] Hintergrundgeräusche
- [ ] Andere: __________________

#### Ressourcen während Call
| Service | CPU (%) | RAM (MB) | Notizen |
|---------|---------|----------|---------|
| LiveKit Server | XX | XXX | |
| LiveKit SIP | XX | XXX | |
| Agent Worker | XX | XXX | |
| Redis | X | XX | |
| Asterisk | X | XX | |
| **Gesamt** | **XX** | **XXXX** | |

#### API-Verbrauch
| Resource | Menge | Einheit | Kosten |
|----------|-------|---------|--------|
| STT-Token | XXX | Token | $X.XX |
| LLM Input-Token | XXX | Token | $X.XX |
| LLM Output-Token | XXX | Token | $X.XX |
| TTS-Zeichen | XXX | Zeichen | $X.XX |
| **Summe** | — | — | **$X.XX** |

#### VAD-Statistik
- VAD-aktiv: [Ja/Nein]
- Sprechpausen erkannt: XX
- STT-Anfragen gesamt: XX
- STT-Anfragen durch VAD gefiltert: XX (XX%)

#### Besonderheiten/Fehler
```
[Hier Auffälligkeiten, Fehlermeldungen oder ungewöhnliche Events notieren]
```

---

## Testfall 2: SIP-Integration (Smartphone)

### SIP-Call #001
**Datum/Uhrzeit**: 2025-12-XX, HH:MM:SS  
**Anruf-Initiator**: [Name/Nummer des Anrufers]  
**DID angerufen**: +49XXXXXXX  
**Netzwerk**: [LAN | WAN | Mobilfunk]

#### SIP-Signalisierung
| Schritt | Status | Timestamp | Notizen |
|---------|--------|-----------|---------|
| INVITE empfangen | ✓/✗ | HH:MM:SS | — |
| Room erstellt | ✓/✗ | HH:MM:SS | z.B. sip-call-abc123 |
| Agent verbunden | ✓/✗ | HH:MM:SS | — |
| RTP Start Anrufer | ✓/✗ | HH:MM:SS | Uplink funktioniert |
| RTP Start Agent (Downlink) | ✓/✗ | HH:MM:SS | **Kritisch!** |
| BYE empfangen | ✓/✗ | HH:MM:SS | Call-Ende |

#### Audio-Qualität (Downlink)
| Aspekt | Status | Bewertung |
|--------|--------|-----------|
| Audio hörbar? | ✓/✗ | [Falls ✗, "stumm" / "Freizeichen nur"] |
| Verständlichkeit | [Exzellent/Gut/Akzeptabel/Schlecht] | MOS: X |
| Natürlichkeit (TTS) | [Sehr natürlich/Ausreichend/Synthetisch] | — |
| Audioartefakte | [Keine/Rauschen/Verzögerung/Dropout] | — |

#### Medien-Pfad Diagnostik
```
docker logs livekit-sip -f (letzte 20 Zeilen nach Call):
[Hier die relevanten Log-Auszüge einfügen]

Agent-Worker Output (letzte 10 Zeilen):
[Hier die Agent-Logs einfügen]

docker stats Snapshot während Call:
[Hier CPU/RAM Werte festhalten]
```

#### Besonderheiten
```
[Fehler, Timeouts, ungewöhnliche Latenzen, RTP-Drops etc.]
```

---

## Testfall 3: Lasttests (parallele Calls)

### Lasttest-Run #001
**Datum/Uhrzeit**: 2025-12-XX, HH:MM:SS  
**Anzahl parallele Calls**: [1 | 2 | 3]  
**Wiederholung**: [1/5 | 2/5 | ...]

#### Parallele Calls (Start gleichzeitig, < 1s Versatz)
| Call-ID | Start-Zeit | Prompt | Latenz | Status |
|---------|-----------|--------|--------|--------|
| Call 1 | HH:MM:SS.mmm | [Mittel] | XXX ms | ✓/✗ |
| Call 2 | HH:MM:SS.mmm | [Mittel] | XXX ms | ✓/✗ |
| Call 3 | HH:MM:SS.mmm | [Mittel] | XXX ms | ✓/✗ |

#### System-Ressourcen (Messinterval: 2s)
| Zeit | CPU (%) | RAM (MB) | Agent-Worker | Fehler |
|------|---------|----------|--------------|--------|
| 00:00 | XX | XXXX | XX% | [API 429 / Timeout / None] |
| 00:02 | XX | XXXX | XX% | |
| 00:04 | XX | XXXX | XX% | |
| 00:06 | XX | XXXX | XX% | |
| 00:08 | XX | XXXX | XX% | |
| **Peak** | **XX** | **XXXX** | **XX%** | |

#### API-Fehler
| Fehlertyp | Anzahl | Betroffen-Call | Zeitpunkt |
|-----------|--------|-----------------|-----------|
| Rate Limit (429) | X | [Call 1/2/3] | HH:MM:SS |
| Timeout | X | [Call 1/2/3] | HH:MM:SS |
| Connection Error | X | [Call 1/2/3] | HH:MM:SS |
| Andere | X | — | — |

#### Erfolgsquote
```
Calls insgesamt:     X/X
Calls erfolgreich:   X/X (XX%)
Calls mit Fehler:    X/X (XX%)
```

#### Besonderheiten
```
[z.B. OpenAI Rate Limit erreicht, Memory Leak erkannt, etc.]
```

---

## Allgemeine Hinweise

### Datenerfassung
- **Agent-Logs**: Automatisch in `logs/agent_worker.log`
- **LiveKit Admin-API**: Nach Call über REST abrufen
- **Docker-Stats**: `docker stats --no-stream > docker_stats_call_XXX.txt`
- **Zeitstempel**: Immer NTP-synchronisiert verwenden

### MOS-Skala Referenz
- **5 (Exzellent)**: Kristallklar, natürlich, keine Artefakte
- **4 (Gut)**: Sehr verständlich, minimale/keine Artefakte
- **3 (Akzeptabel)**: Verständlich, aber leichte Verzerrungen/Latenzbuckel
- **2 (Schlecht)**: Verständlichkeit beeinträchtigt
- **1 (Sehr Schlecht)**: Unverstehbar/nicht nutzbar

### Fehlerbehandlung
Falls ein Call fehlschlägt:
1. Fehler-Typ identifizieren (API, Netzwerk, Agent-Crash)
2. Logs komplett speichern: `docker logs livekit > livekit_ERROR_XXX.log`
3. Call-Nummer notieren, in Protokoll kennzeichnen
4. Falls möglich: 30s warten → Retry durchführen

### Datenspeicherung
```
evaluation/results/
├── webui_call_001.json     (objektive Metriken)
├── webui_call_001_mos.txt  (subjektive Bewertung)
├── sip_call_001.json
├── sip_call_001_mos.txt
├── load_test_run_1.csv
└── ...
```

---

**Viel Erfolg bei der Evaluation!** 🚀

