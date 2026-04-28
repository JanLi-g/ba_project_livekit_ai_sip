# 01 - LLM-Zeitmessung im Kolloquium erklären

## Kernaussage
- Der Agent funktioniert im Gespräch.
- STT und TTS Latenzen werden gespeichert.
- LLM-Latenz ist in den vorhandenen Metrik-Dateien inkonsistent bzw. `null`.
- Das ist kein Total-Ausfall des Agents, sondern ein Instrumentierungsproblem.

## Beleg aus euren echten Metriken
- In `metrics/sip-call-{callID}_1767357568.json` steht `avg_llm_latency: null` und `llm_calls: []`.
- In `metrics/sip-call-{callID}_1767357568.ndjson` ist `llm_latency` pro Turn ebenfalls `null`.
- Gleichzeitig sind `stt_latency` und teilweise `tts_latency` vorhanden.

## Wie du das einfach erklärst
"Die LLM-Antwort kommt an, aber unsere Zeitmessung greift dort nicht sauber. Bei STT/TTS klappt das Patchen stabiler. LLM-Calls sind oft tiefer im SDK-Flow (async, interne Methoden, mögliche Retries/Streams), dadurch ist das Messen von außen schwieriger."

## Gute, ehrliche Antwort auf Rückfragen
- "Die Funktion (Antwortgenerierung) läuft, nur das Timing wird nicht robust aufgezeichnet."
- "Das ist ein typisches Produktions-Thema: Monitoring-Integration ist bei LLM oft komplexer als bei STT/TTS."
- "Nächster Schritt wäre direktere SDK-Instrumentierung statt reinem Monkey-Patch."

## Was du NICHT behaupten solltest
- Keine feste durchschnittliche LLM-Latenz nennen, wenn sie in den Logs `null` ist.
- Kein vollständig valides Token-Controlling behaupten.

## Ein Satz für die Folie
"LLM funktioniert funktional, aber die aktuelle LLM-Zeitmessung ist in unseren Realdaten noch nicht robust genug für belastbare KPI-Aussagen."

