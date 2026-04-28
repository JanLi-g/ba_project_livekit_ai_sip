# Messproblem: `llm_latency = null` in `python/agent_worker.py`

---

## Kontext
Der Voice-Agent in `python/agent_worker.py` startet über `main()`, verarbeitet Calls in `entrypoint(...)` und speichert Metriken als NDJSON/JSON. Ziel sind STT-, LLM- und TTS-Latenzen pro Turn.

## Beobachtetes Problem
In den Turn-Metriken und in der Summary ist `llm_latency` häufig `null`, obwohl der Agent funktional antwortet.

## Technische Ursachen

### Ursache A: LLM-Wrapper wird als Coroutine statt Callable gesetzt
In `entrypoint(...)` ist die Wrapper-Fabrik als `async def` definiert.

```python
async def create_llm_wrapper(...): ...
setattr(orig_llm, method_name, create_llm_wrapper(...))
```

Bei `setattr(...)` wird damit nicht direkt eine Funktion, sondern zunächst ein Coroutine-Objekt gesetzt. Dadurch wird die LLM-Instrumentierung unzuverlässig.

### Ursache B: Turn-Persistenz feuert zeitlich zu früh
`on_user_transcript(...)` wird über den Log-Hook `received user transcript` ausgelöst. Das passiert oft nach STT, aber vor Abschluss von LLM/TTS im selben Turn.
Folge: `llm_latency`/`tts_latency` sind beim Schreiben oft noch `0.0` und werden als `None` persistiert.

### Ursache C: Gepatchte LLM-Methoden können am realen Call-Pfad vorbeigehen
Der Code patcht `chat`, `agentic_loop_call`, `__call__`. Nutzt das SDK intern andere Pfade, wird keine LLM-Latenz erfasst.

## Messkonsequenz
- STT-Latenz ist plausibel messbar.
- LLM-Latenz ist aktuell nicht belastbar für KPI-Aussagen.
- TTS-Latenz ist teilweise vorhanden, aber turn-zugeordnet nicht immer konsistent.

## Hinweis zu TTS in NDJSON
- In manchen `.ndjson`-Dateien ist bei Turn 1 `tts_latency: null`, während in der `.json` unter `tts_calls` bereits TTS-Werte vorhanden sind.
- Ursache: Der Turn wird in `on_user_transcript(...)` geschrieben, bevor TTS im selben Turn sicher fertig ist.
- Die TTS-Latenz wird erst beim Verlassen des TTS-Context gesetzt; dadurch kann die Turn-Zeile bereits persistiert sein.
- `tts_calls` zählt zudem auch Nicht-Turn-Audio (z. B. Begrüßung), daher können Anzahl und Zuordnung gegenüber `eou_metrics` abweichen.

**Kurzsatz für die Verteidigung:**
`tts_latency` in NDJSON kann teilweise `null` sein, weil Turn-Datensätze beim Transcript-Event geschrieben werden und TTS erst danach final gemessen wird. Deshalb ist `tts_calls` auf Komponentenebene oft vollständiger als die Turn-Zuordnung.

## Fix-Plan
1. **Wrapper korrekt binden:** Wrapper-Fabrik als `def` implementieren, danach per `setattr` setzen.
2. **Turn-Abschluss definieren:** Turn erst persistieren, wenn STT + LLM + TTS für denselben Turn vorliegen.
3. **API-nahe LLM-Erfassung:** Messung direkt am OpenAI-Request/Response statt nur über Turn-Hook/Log-Parsing.
4. **Schemas trennen:** Turn-Metriken und komponentenbezogene API-Call-Metriken klar trennen.

## Lösungsergänzung: OpenAI-API-nahe LLM-Metriken
- **Messpunkt verlagern:** LLM-Latenz direkt vor/nach dem echten OpenAI-Client-Aufruf messen und sofort in `record_llm(...)` persistieren.
- **Pro Call loggen:** `model`, `latency_ms`, `tokens_in`, `tokens_out`, `timestamp`, `status`; zusätzlich `request_id` für saubere Nachverfolgung.
- **Turn-Zuordnung sauber halten:** API-Call-Daten (`llm_calls`) getrennt von Turn-Daten (`record_eou`) speichern und über `turn` oder `request_id` verknüpfen.
- **Praxisgrenze transparent machen:** `usage`/Tokenwerte können je nach SDK-/Modellpfad in Einzelfällen fehlen (best effort), Latenz bleibt trotzdem messbar.
- **Nutzen:** `avg_llm_latency` wird deutlich robuster, und Token-Auswertungen sind für KPI-Fragen belastbarer.

## Rückfrage-Antwort (kurz, präsentationstauglich)
"Ja, wir können LLM-Calls und Tokens robuster erfassen, wenn wir direkt API-nah am OpenAI-Request/Response instrumentieren statt nur über den Turn-Hook."

## Verifikationsplan nach Fix
- 10 Testcalls mit je 3-5 Turns.
- Erwartung: `avg_llm_latency` nicht mehr `null`, `llm_calls` > 0, konsistente STT/LLM/TTS-Werte pro Turn.
- Abweichungen als Bug-Report mit Call-ID dokumentieren.

## Kurzfazit
Der Agent funktioniert funktional, die LLM-Zeitmessung ist aktuell aber nicht belastbar.
Nach Instrumentierungs-Fix und Verifikationslauf können belastbare LLM-KPIs nachgezogen werden.
