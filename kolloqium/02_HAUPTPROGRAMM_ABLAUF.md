# 02 - Hauptablauf des Agent Workers

## Ablauf in 4 Schritten
1. **Prewarm**
    - In `python/agent_worker.py` lädt `prewarm()` die VAD (`silero.VAD.load()`).
2. **Entrypoint / Session Start**
   - `entrypoint()` baut den Agent mit STT (`openai.STT`), LLM (`openai.LLM`) und TTS (`openai.TTS`).
    - Verbindung zum LiveKit-Room, Session Start, Begrüßung.
3. **Laufender Call**
   - Event-basiert: Teilnehmer verbinden/trennen.
   - Turn-basiert: Nutzer spricht -> STT -> LLM -> TTS.
   - `on_user_transcript()` sammelt Turn-Daten und schreibt NDJSON.
4. **Call-Ende / Summary**
   - `usage_collector.summarize()` aggregiert Kennzahlen.
   - Ausgabe in JSON + Log.

## Wichtige Code-Stellen (für Walkthrough)
- `UsageCollector` (Sammeln/Aggregieren)
- `prewarm()`
- `entrypoint()`
- STT/LLM/TTS Patch-Blöcke
- `on_user_transcript()`
- `summarize()` / `log_summary()`

## Einfache Story für die Präsentation
"Der Worker tritt dem Room bei, hört zu, verarbeitet jeden Turn und schreibt danach strukturiert Metriken weg. Das passiert pro Call isoliert und reproduzierbar."

## Was du hervorheben kannst
- Stabile STT/TTS-Messung vorhanden.
- LLM-Messung aktuell noch nicht robust (siehe `01_LLM_ZEITMESSUNG.md`).
- Persistenz erfolgt turnweise (`.ndjson`) und callweise (`.json`).

