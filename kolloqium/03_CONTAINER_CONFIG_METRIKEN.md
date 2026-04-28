# 03 - Container, Config-Dateien und Metrik-Erfassung

## Container-Zusammenhang (aus `docker-compose.yml`)
- `asterisk`: SIP-Einstieg (Port 5060/udp), Dialplan/Trunk.
- `livekit`: Medien- und Room-Server (7880/7881/7882 + RTP-Range).
- `livekit-sip`: SIP-Bridge zwischen Telefonie und LiveKit.
- `redis`: Zustand/Koordination für SIP/LiveKit-Komponenten.
- `voice-agent`: Python Worker mit `python/agent_worker.py`.

Kurzfluss:
`Telefonnetz/SIP -> asterisk -> livekit-sip -> livekit room -> voice-agent`

## Welche Config zu welchem Container gehört
- `livekit-config.yaml` -> `livekit`
  - Ports/RTC-Bereich, Redis-Adresse, API-Keys.
- `sip-config.yaml` -> `livekit-sip`
  - Verbindung zu LiveKit (`ws_url`, API-Key/Secret), Redis.
- `asterisk/pjsip.conf` -> `asterisk`
  - SIP-Transport, Trunk/Endpoints.
- `asterisk/extensions.conf` -> `asterisk`
  - Dialplan (Weiterleitung Richtung LiveKit-SIP Endpoint).

## Wie Metriken gespeichert werden
- In `python/agent_worker.py` wird unter `metrics/` geschrieben.
- Pro Turn: `*.ndjson` (append pro Sprecherwechsel).
- Pro Call: `*.json` (aggregierte Zusammenfassung).

Beispielinhalt pro Turn (NDJSON):
- `transcript`
- `stt_latency`
- `llm_latency` (aktuell oft `null`)
- `tts_latency`

Beispielinhalt pro Call (JSON):
- `duration_sec`, `turns`
- `avg_stt_latency`, `avg_llm_latency`, `avg_tts_latency`
- `llm_calls`, `tts_calls`

## Wichtiger Präsentationsteil
- Erkläre den Unterschied zwischen **funktionalem Ablauf** (Agent antwortet) und **Messqualität** (LLM-Latenz noch nicht robust).
- Zeige 1 JSON + 1 NDJSON aus `metrics/` als Beleg.

