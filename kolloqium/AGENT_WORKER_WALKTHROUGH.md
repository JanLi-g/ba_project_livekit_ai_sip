# Code-Walkthrough (5-Minuten-Version): `python/agent_worker.py`

Dieses Handout ist auf einen kurzen, vorlesbaren Ablauf reduziert: nur die wichtigsten Code-Pfade mit Zeilenangaben.

---

## 1) Bootstrapping, Imports, Metrikobjekt

**Was passiert:**
- Imports und Basiskonfiguration laden die Bausteine für LiveKit, OpenAI, STT/TTS und Logging. (`agent_worker.py`: 7-27, 151-167)
- `UsageCollector` ist die zentrale Sammelstelle für Turn-, LLM- und TTS-Metriken. (`agent_worker.py`: 28-149)
- `prewarm(...)` lädt VAD einmalig, damit der Call-Start stabiler und schneller ist. (`agent_worker.py`: 170-183)

---

## 2) Einstieg pro Call und Session-Start

**Was passiert:**
- `entrypoint(...)` initialisiert Call-ID, Dateipfade und Zustandsvariablen. (`agent_worker.py`: 185-210, 245-267)
- Agent-Pipeline wird aufgebaut (`STT`, `LLM`, `TTS`) und Session gestartet. (`agent_worker.py`: 230-236, 349-359)
- Teilnehmer-Events plus Begrüßung starten den eigentlichen Gesprächsfluss. (`agent_worker.py`: 272-286, 366-371)

---

## 3) Laufzeit-Messung in STT, LLM und TTS

**Was passiert:**
- STT-Wrapper misst Erkennungsdauer und Timeouts. (`agent_worker.py`: 378-397)
- LLM-Wrapper versucht Antwortlatenz und ggf. Usage/Tokens zu erfassen. (`agent_worker.py`: 405-456)
- TTS-Wrapper misst Synthesezeit und Audio-Umfang; Daten gehen in `pending_turn_data` und `UsageCollector`. (`agent_worker.py`: 460-560)

---

## 4) Turn-Bildung und Persistenz

**Was passiert:**
- `on_user_transcript(...)` baut aus den gepufferten Messwerten einen Turn-Datensatz. (`agent_worker.py`: 567-612)
- Turn wird in zwei Ziele geschrieben: `record_eou(...)` (Aggregat) und `.ndjson` (Rohereignisse). (`agent_worker.py`: 605-612, 617-631)
- Danach wird der Turn-Puffer zurückgesetzt, damit der nächste Turn sauber startet. (`agent_worker.py`: 636-640)

---

## 5) Abschluss, Summary, Fallback

**Was passiert:**
- `log_summary(...)` schreibt die finale `.json`-Zusammenfassung. (`agent_worker.py`: 716-777, 721-724)
- Beim Session-Ende wird Abschlusslogik ausgeführt; im Fehlerfall greift `finally` als Fallback. (`agent_worker.py`: 780-790, 797-807)
- `main()` bindet `entrypoint` und `prewarm` an den Worker-Prozess. (`agent_worker.py`: 810-830)

---
