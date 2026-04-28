# Diskussion: KPI-Hinweise und aktuelle Messgrenzen

Dieses Dokument fasst die Diskussionspunkte für die Verteidigung zusammen.

---

## Hinweis zu den KPIs
- LLM-Calls und Token-Ausgabe robuster machen.
- Datenbankanbindung für größere Datenmengen einplanen.
- Code-Struktur verbessern.
- Statt reiner API-Anbindung: lokales Modell explizit für Use Cases trainieren.
- Rechtliche Beratung und Compliance (z. B. wie bei Telekom-Umfeldern) früh prüfen.

## Hinweis zur LLM-Latenz im aktuellen Stand

**Code-Zeilen:** 287-348, 405-456, 567-640, 647-690

**Was hier wichtig ist:**
- Die LLM-Antwort kommt an, aber die Messung greift dort nicht sauber.
- Bei STT/TTS klappt das Patchen stabiler. LLM-Calls liegen oft tiefer im SDK-Flow (async, interne Methoden, mögliche Retries/Streams), dadurch ist Messen von außen schwieriger.
- `on_user_transcript(...)` ist im `entrypoint` doppelt deklariert (erst 287-348, später 567-640); die zweite Definition überschreibt die erste.
- Dadurch kann das Laufzeitverhalten schwerer nachvollziehbar werden und die Metrikzuordnung zusätzlich erschweren.
- Deshalb kann `llm_latency` in den Turn-Daten häufig `null` sein, obwohl der Agent funktional antwortet.
- Das ist eine Monitoring-Limitation, kein funktionaler Ausfall des Agents.

**Ergänzung (OpenAI-API-nahe Erfassung):**
- LLM-Call-Latenz und `usage` direkt am API-Request/Response abgreifen statt nur über den Turn-Hook.
- Dabei pro Call mindestens `model`, `latency_ms`, `tokens_in`, `tokens_out`, `timestamp`, `status` loggen; `request_id` ist zusätzlich hilfreich.
- Wichtig für die Präsentation: Token/Usage sind je nach SDK-/Modellpfad teils "best effort" und können in Einzelfällen fehlen.
- Praktischer nächster Schritt: Instrumentierung an die tiefere OpenAI-Client-Schicht verlagern und dann in `record_llm(...)` konsistent persistieren.
- Im aktuellen Stand messen wir viel über Laufzeit-Patches und Transcript-Trigger. Das funktioniert für STT/TTS stabiler, bei LLM aber nicht immer konsistent, weil Calls tiefer im SDK-Flow liegen. API-nahe würden wir pro Request/Response direkt `model`, `latency_ms`, `tokens_in`, `tokens_out`, `timestamp` und `status` erfassen und dann in `record_llm(...)` persistieren.

## Hinweis zu TTS in NDJSON
- In manchen `.ndjson` ist bei Turn 1 `tts_latency: null`, während in `.json` unter `tts_calls` bereits TTS-Werte vorhanden sind.
- Das passt zum Ablauf in `python/agent_worker.py`: Der Turn wird in `on_user_transcript(...)` gespeichert, bevor TTS im selben Turn sicher fertig ist.
- TTS-Latenz wird erst beim Verlassen des TTS-Context gesetzt. Dadurch kann die Turn-Zeile schon geschrieben sein und TTS kommt zu spät.
- Zusätzlich zählt `tts_calls` auch Nicht-Turn-Audio (z. B. Begrüßung), daher können Anzahl/Zuordnung gegenüber `eou_metrics` abweichen.

**Kernaussage für Rückfragen:**
`tts_latency` in NDJSON kann teilweise `null` sein, weil Turn-Datensätze beim Transcript-Event geschrieben werden und TTS erst danach final gemessen wird. Deshalb ist `tts_calls` vollständiger auf Komponentenebene, während Turn-Zuordnung aktuell noch zeitlich versetzt sein kann.

