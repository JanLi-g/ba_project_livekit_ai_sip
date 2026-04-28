"""
LiveKit Voice Agent Worker - Optimierte Version v3

Verwendet: livekit.agents.voice.Agent mit umfassendem Metrics-Tracking
"""

import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import re
import json

from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.plugins import openai, silero


class UsageCollector:
    """Sammelt und aggregiert Metriken für Voice Agent Calls"""

    def __init__(self, call_id: str, room: str):
        self.call_id = call_id
        self.room = room
        self.start_ts = time.time()
        self.participants = set()
        self.eou_metrics = []
        self.stt_timeouts = 0
        self.llm_calls = []
        self.tts_calls = []
        self.agent_startup_latency = None  # Agent Init bis Greeting
        self.disconnect_reason = None
        self.disconnect_participant = None
        self.disconnect_time = None

    def add_participant(self, participant_id: str):
        if participant_id:
            self.participants.add(str(participant_id))

    def record_agent_startup(self, latency: float):
        """Speichere Agent-Startup-Latenz"""
        self.agent_startup_latency = latency

    def record_eou(self, turn: int, transcript: str, **kwargs):
        """Erfasse End-of-Utterance Metrik mit optionalen Latenzen"""
        self.eou_metrics.append({
            'turn': turn,
            'transcript': transcript,
            'transcript_delay': kwargs.get('transcript_delay'),
            'stt_latency': kwargs.get('stt_latency'),
            'llm_latency': kwargs.get('llm_latency'),
            'tts_latency': kwargs.get('tts_latency'),
            'ts': time.time()
        })

    def record_stt_timeout(self):
        self.stt_timeouts += 1

    def record_llm(self, latency: float, **kwargs):
        self.llm_calls.append({
            'latency': latency,
            'model': kwargs.get('model'),
            'tokens_in': kwargs.get('tokens_in'),
            'tokens_out': kwargs.get('tokens_out'),
            'ts': time.time()
        })

    def record_tts(self, latency: float, **kwargs):
        self.tts_calls.append({
            'latency': latency,
            'audio_bytes': kwargs.get('audio_bytes'),
            'audio_seconds': kwargs.get('audio_seconds'),
            'ts': time.time()
        })

    def record_disconnect(self, reason: str | None, participant: str | None):
        self.disconnect_reason = reason
        self.disconnect_participant = participant
        self.disconnect_time = time.strftime('%Y-%m-%d %H:%M:%S')

    def _calculate_average(self, metrics, key):
        """Hilfsfunktion für Durchschnittsberechnung"""
        values = [m.get(key) for m in metrics if m.get(key) and m.get(key) > 0]
        return sum(values) / len(values) if values else None

    def summarize(self):
        """Erstelle finale Zusammenfassung aller Metriken"""
        duration = time.time() - self.start_ts

        return {
            'call_id': self.call_id,
            'room': self.room,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_ts)),
            'end_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_sec': round(duration, 2),
            'participants': list(self.participants),
            'turns': len(self.eou_metrics),
            'stt_timeouts': self.stt_timeouts,
            'avg_stt_latency': self._calculate_average(self.eou_metrics, 'stt_latency'),
            'avg_llm_latency': self._calculate_average(self.eou_metrics, 'llm_latency'),
            'avg_tts_latency': self._calculate_average(self.eou_metrics, 'tts_latency'),
            'agent_startup_latency': self.agent_startup_latency,
            'total_tts_bytes': sum((x.get('audio_bytes') or 0) for x in self.tts_calls),
            'total_tts_seconds': sum((x.get('audio_seconds') or 0) for x in self.tts_calls),
            'eou_metrics': self.eou_metrics,
            'llm_calls': self.llm_calls,
            'disconnect_reason': self.disconnect_reason,
            'disconnect_participant': self.disconnect_participant,
            'disconnect_time': self.disconnect_time,
        }

# Logging konfigurieren (Unicode-freundlich für Windows)
class AsciiOnlyStreamHandler(logging.StreamHandler):
    """Stream-Handler der Emojis für die Konsole entfernt"""
    def emit(self, record):
        if isinstance(record.msg, str):
            record.msg = re.sub(r'[^\x00-\x7F]+', '', record.msg)
        super().emit(record)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("agent_worker_debug.log", encoding="utf-8"),
        AsciiOnlyStreamHandler()
    ]
)
logger = logging.getLogger("voice-agent")


def prewarm(proc: JobProcess):
    """Lädt alle schweren Ressourcen VOR dem ersten Job"""
    logger.info("🔧 Prewarm: Lade VAD und Agent-Komponenten...")
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("✅ Prewarm abgeschlossen")


async def entrypoint(ctx: JobContext):
    """Hauptfunktion des Voice Agents"""

    # Initialisiere Metriken-Variablen
    call_start_ts = time.time()
    greeting_sent_ts = None  # Wird gesetzt wenn Greeting gesendet wird
    pending_turn_data = {'llm_latency': None, 'tts_latency': None}
    summary_written = False
    metrics_logging_enabled = False

    try:
        room_name = ctx.room.name
        is_sip_call = room_name.startswith("sip-call")

        # UsageCollector mit korrekten Parametern initialisieren
        call_id = f"{room_name}_{int(call_start_ts)}"
        usage_collector = UsageCollector(call_id=call_id, room=room_name)

        if is_sip_call:
            logger.info(f"📞 SIP-CALL erkannt: {room_name}")
            instructions = (
                "Du bist ein hilfreicher deutscher Sprach-Assistent am Telefon. "
                "Sprich klar und deutlich. Halte Antworten kurz und präzise. "
                "Der Nutzer ruft über eine Telefonleitung an."
            )
            greeting = "Hallo! Wie kann ich Ihnen helfen?"
        else:
            logger.info(f"🌐 WEB-CALL erkannt: {room_name}")
            instructions = "Du bist ein hilfreicher deutscher Sprach-Assistent. Antworte freundlich und präzise auf Deutsch."
            greeting = "Hallo! Ich bin Ihr Sprach-Assistent. Wie kann ich Ihnen helfen?"

        logger.info("🤖 Erstelle Agent...")
        agent = Agent(
            instructions=instructions,
            vad=ctx.proc.userdata["vad"],
            stt=openai.STT(language="de"),
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=openai.TTS(voice="alloy"),
        )
        logger.info("✅ Agent erstellt")

        # === LLM LATENZ TRACKING ===
        # Patche die chat() Methode des LLM direkt nach Erstellung.
        # chat() muss ein Async-Context-Manager bleiben (async with ...)
        orig_llm = agent.llm
        if hasattr(orig_llm, 'chat'):
            orig_chat = orig_llm.chat

            class _ChatContextWrapper:
                """Async-Context-Manager Wrapper, der LLM-Latenz misst."""
                def __init__(self, *args, **kwargs):
                    self._args = args
                    self._kwargs = kwargs
                    self._cm = None
                    self._start = None
                    self._recorded = False
                    self._model = getattr(orig_llm, 'model', None)

                def _record_latency(self):
                    if self._recorded or self._start is None:
                        return
                    llm_latency = time.perf_counter() - self._start
                    pending_turn_data['llm_latency'] = llm_latency
                    usage_collector.record_llm(latency=llm_latency, model=self._model)
                    logger.debug(f"[LLM-CALL] latency={llm_latency:.3f}s")
                    self._recorded = True

                async def __aenter__(self):
                    self._start = time.perf_counter()
                    self._cm = orig_chat(*self._args, **self._kwargs)
                    entered = await self._cm.__aenter__()

                    if hasattr(entered, '__aiter__'):
                        wrapper_self = self

                        class _AsyncIterWrapper:
                            def __init__(self, inner):
                                self._inner = inner
                                self._first = True

                            def __aiter__(self):
                                return self

                            async def __anext__(self):
                                try:
                                    item = await self._inner.__anext__()
                                except Exception:
                                    wrapper_self._record_latency()
                                    raise
                                if self._first:
                                    wrapper_self._record_latency()
                                    self._first = False
                                return item

                        return _AsyncIterWrapper(entered)

                    # Fallback: kein Async-Iterator -> Latenz beim Enter messen
                    self._record_latency()
                    return entered

                async def __aexit__(self, exc_type, exc, tb):
                    self._record_latency()
                    return await self._cm.__aexit__(exc_type, exc, tb)

            def chat_with_latency(*args, **kwargs):
                return _ChatContextWrapper(*args, **kwargs)

            orig_llm.chat = chat_with_latency

        logger.info("⚡ Verbinde mit Room und starte Session...")

        # === WICHTIG: Verbinde mit Room VOR Session-Start ===
        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        logger.info("✅ Room verbunden!")

        # Evaluierungs-Tracking: Verzeichnis und Dateien für Metriken
        metrics_dir = Path.cwd() / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Metrics directory ready at: {metrics_dir}")

        metrics_ndjson = metrics_dir / f"{call_id}.ndjson"
        metrics_json = metrics_dir / f"{call_id}.json"

        # Turn-Tracking Variablen
        turn_counter = 0
        last_turn_time = time.perf_counter()

        # Erstelle Session ZUERST (wird vom Handler benötigt)
        session = AgentSession()

        # Event-Handler Registration (NACH Session-Erstellung!)
        @ctx.room.on("participant_connected")
        def on_participant_joined(participant):
            """Handler: Neuer Teilnehmer verbunden"""
            if participant:
                usage_collector.add_participant(participant_id=participant.identity)
                logger.info(f"[LIVEKIT] participant_connected: {participant.identity}")

        @ctx.room.on("participant_disconnected")
        def on_participant_disconnected(participant):
            """Handler: Teilnehmer getrennt"""
            participant_id = participant.identity if participant else None
            logger.info(f"[LIVEKIT] participant_disconnected: {participant_id}")
            usage_collector.record_disconnect(reason="CLIENT_INITIATED", participant=participant_id)
            setattr(session, 'closed', True)


        # Erfasse bereits verbundene Participants
        for participant in ctx.room.remote_participants.values():
            usage_collector.add_participant(participant_id=participant.identity)
            logger.info(f"[LIVEKIT] existing participant found: participant={participant.identity}")

        # Starte Session
        await session.start(agent=agent, room=ctx.room)
        logger.info("✅ Session gestartet")

        # Überprüfe auf neue Participants nach Session-Start
        await asyncio.sleep(0.2)
        for participant in ctx.room.remote_participants.values():
            usage_collector.add_participant(participant_id=participant.identity)

        # === STT LATENZ TRACKING ===
        # Patche STT: Tracke Timeouts und Latenz (VOR Begrüßung für vollständiges Tracking)
        orig_stt = agent.stt
        if hasattr(orig_stt, 'recognize'):
            orig_recognize = orig_stt.recognize

            async def recognize_with_timeout_count(*args, **kwargs):
                """Wrapper um STT recognize() zum Tracken von Timeouts"""
                nonlocal pending_turn_data
                start = time.perf_counter()
                try:
                    result = await orig_recognize(*args, **kwargs)
                    pending_turn_data['stt_latency'] = time.perf_counter() - start
                    return result
                except Exception as e:
                    pending_turn_data['stt_latency'] = time.perf_counter() - start
                    if e.__class__.__name__ == 'APITimeoutError':
                        usage_collector.record_stt_timeout()
                    raise

            orig_stt.recognize = recognize_with_timeout_count

        # === TTS LATENZ TRACKING ===
        # Patche TTS: Tracke Latenz und Audio-Bytes (VOR Begrüßung für vollständiges Tracking)
        orig_tts = agent.tts
        if hasattr(orig_tts, 'synthesize'):
            orig_synthesize = orig_tts.synthesize

            class AudioStreamWrapper:
                """Wrapper um TTS-Audio-Stream zum Zählen von Bytes"""
                def __init__(self, stream_obj):
                    self._stream = stream_obj
                    self.bytes_count = 0
                    self.frames_count = 0
                    self.audio_seconds = 0.0

                def __getattr__(self, name):
                    return getattr(self._stream, name)

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    if not hasattr(self, '_iterator'):
                        if hasattr(self._stream, '__aiter__'):
                            self._iterator = self._stream.__aiter__()
                        elif hasattr(self._stream, 'iter_bytes'):
                            self._iterator = self._stream.iter_bytes()
                        elif hasattr(self._stream, 'aiter_bytes'):
                            self._iterator = self._stream.aiter_bytes()
                        else:
                            raise StopAsyncIteration

                    try:
                        chunk = await self._iterator.__anext__()
                        self.frames_count += 1

                        # Extrahiere Bytes aus verschiedenen Audio-Objekt-Formaten
                        try:
                            if hasattr(chunk, 'frame'):
                                # SynthesizedAudio mit .frame (RTCAudioFrame)
                                frame = chunk.frame
                                if hasattr(frame, 'data'):
                                    self.bytes_count += len(frame.data)
                                    # Berechne Audiodauer aus Sample-Rate
                                    if hasattr(frame, 'sample_rate') and hasattr(frame, 'samples_per_channel'):
                                        self.audio_seconds += frame.samples_per_channel / frame.sample_rate
                            elif hasattr(chunk, 'data'):
                                # Direktes .data Attribut
                                audio_data = chunk.data
                                if hasattr(audio_data, 'data'):
                                    self.bytes_count += len(audio_data.data)
                                elif isinstance(audio_data, bytes):
                                    self.bytes_count += len(audio_data)
                            elif isinstance(chunk, bytes):
                                self.bytes_count += len(chunk)
                        except Exception as e:
                            logger.debug(f"[TTS-WRAPPER] Error extracting audio bytes: {e}")

                        return chunk
                    except StopAsyncIteration:
                        raise

            class SynthesizeWithLatency:
                """Context Manager für TTS mit Latenz-Messung"""
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs
                    self._cm = None
                    self._start = None
                    self._entered = None

                async def __aenter__(self):
                    self._start = time.perf_counter()
                    self._cm = orig_synthesize(*self.args, **self.kwargs)
                    entered = await self._cm.__aenter__()
                    try:
                        wrapper = AudioStreamWrapper(entered)
                        self._entered = wrapper
                        return wrapper
                    except Exception:
                        self._entered = entered
                        return entered

                async def __aexit__(self, exc_type, exc, tb):
                    try:
                        return await self._cm.__aexit__(exc_type, exc, tb)
                    finally:
                        tts_latency = time.perf_counter() - self._start
                        pending_turn_data['tts_latency'] = tts_latency

                        # Hole Audio-Metriken aus dem Wrapper
                        audio_bytes = getattr(self._entered, 'bytes_count', None) if self._entered else None
                        audio_seconds = getattr(self._entered, 'audio_seconds', None) if self._entered else None

                        # Filtere Null-Werte
                        if audio_bytes is not None and audio_bytes == 0:
                            audio_bytes = None
                        if audio_seconds is not None and audio_seconds == 0.0:
                            audio_seconds = None

                        usage_collector.record_tts(latency=tts_latency, audio_bytes=audio_bytes, audio_seconds=audio_seconds)
                        logger.debug(f"[TTS-PATCH] latency={tts_latency:.3f}s, bytes={audio_bytes}, seconds={audio_seconds}")

            def synthesize_with_latency(*args, **kwargs):
                return SynthesizeWithLatency(*args, **kwargs)

            orig_tts.synthesize = synthesize_with_latency

        # === BEGRÜSSUNG SENDEN (jetzt mit allen Patches aktiv) ===
        # Hier werden STT und TTS bereits gemessen
        await asyncio.sleep(1)
        logger.info("🗣️ Sende Begrüßung...")
        await session.say(greeting, allow_interruptions=True)
        greeting_sent_ts = time.time()
        logger.info("✅ Begrüßung gesendet")

        # Berechne Agent-Startup Latenz
        agent_startup_latency = greeting_sent_ts - call_start_ts
        logger.info(f"[METRICS] Agent-Startup-Latenz: {agent_startup_latency:.3f}s")
        usage_collector.record_agent_startup(agent_startup_latency)

        # === RESET UND VORBEREITUNG FÜR USER-TRANSKRIPTE ===
        # Reset pending_turn_data nach Begrüßung für saubere User-Turn Metriken
        pending_turn_data = {
            'stt_latency': 0.0,
            'llm_latency': 0.0,
            'tts_latency': 0.0,
            'transcript': None,
            'transcript_delay': None
        }

        # Aktiviere Metrics-Logging für User-Inputs
        metrics_logging_enabled = True
        logger.debug("[METRICS] Metrics logging enabled - will record user transcripts")
        logger.info("🎤 Agent läuft und wartet auf User Input")

        def on_user_transcript(transcript: str, transcript_delay: float = None):
            """Erfasse und logge Turn-Metriken wenn User spricht"""
            nonlocal turn_counter, last_turn_time, pending_turn_data
            if not metrics_logging_enabled:
                return

            turn_counter += 1
            now = time.perf_counter()
            turn_duration = now - last_turn_time
            last_turn_time = now

            # Hole Latenzen aus pending_turn_data
            stt_lat = pending_turn_data.get('stt_latency', 0.0) or 0.0
            llm_lat = pending_turn_data.get('llm_latency', 0.0) or 0.0
            tts_lat = pending_turn_data.get('tts_latency', 0.0) or 0.0

            # Logge Live-Metriken
            logger.info("="*60)
            logger.info(f"LIVE METRIK - Turn {turn_counter}")
            logger.info(f"  Transcript: {transcript}")
            logger.info(f"  Turn-Dauer: {turn_duration:.2f}s")
            if transcript_delay:
                logger.info(f"  Transcript-Delay: {transcript_delay:.3f}s")
            logger.info(f"  STT-Latenz: {stt_lat:.3f}s")
            logger.info(f"  LLM-Latenz: {llm_lat:.3f}s")
            logger.info(f"  TTS-Latenz: {tts_lat:.3f}s")
            logger.info("="*60)

            # Speichere im UsageCollector
            usage_collector.record_eou(
                turn=turn_counter,
                transcript=transcript,
                transcript_delay=transcript_delay,
                stt_latency=stt_lat if stt_lat > 0 else None,
                llm_latency=llm_lat if llm_lat > 0 else None,
                tts_latency=tts_lat if tts_lat > 0 else None
            )

            # Speichere Turn in NDJSON-Datei
            try:
                obj = {
                    'call_id': call_id,
                    'turn': turn_counter,
                    'transcript': transcript,
                    'transcript_delay': transcript_delay,
                    'stt_latency': stt_lat if stt_lat > 0 else None,
                    'llm_latency': llm_lat if llm_lat > 0 else None,
                    'tts_latency': tts_lat if tts_lat > 0 else None,
                    'ts': time.time()
                }
                with open(metrics_ndjson, 'a', encoding='utf-8') as mf:
                    mf.write(json.dumps(obj, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.debug(f"Failed to write turn metrics: {e}")

            # Setze Latenzen zurück für nächsten Turn
            pending_turn_data['stt_latency'] = 0.0
            pending_turn_data['llm_latency'] = 0.0
            pending_turn_data['tts_latency'] = 0.0
            pending_turn_data['transcript'] = None
            pending_turn_data['transcript_delay'] = None

        # === TRANSCRIPT-HANDLER: Fange User-Transkripte aus LiveKit auf ===
        class LivekitTranscriptHandler(logging.Handler):
            """Handler zum Abfangen von User-Transkripten aus LiveKit Logger"""
            def __init__(self):
                super().__init__()

            def emit(self, record):
                """Verarbeite Log-Einträge und extrahiere User-Transkripte"""
                nonlocal metrics_logging_enabled
                if not metrics_logging_enabled:
                    return

                try:
                    msg = record.getMessage() if hasattr(record, 'getMessage') else str(record.msg)
                    if 'received user transcript' not in msg:
                        return

                    transcript_text = None
                    transcript_delay = None

                    # Versuche zuerst aus record-Attributen zu extrahieren
                    transcript_text = getattr(record, 'user_transcript', None)
                    transcript_delay = getattr(record, 'transcript_delay', None)

                    # Fallback: Extrahiere aus Log-Nachricht mit Regex
                    if not transcript_text and msg:
                        m = re.search(r'"user_transcript"\s*:\s*"([^"]+)"', msg)
                        if m:
                            transcript_text = m.group(1)

                        if not transcript_delay:
                            m = re.search(r'"transcript_delay"\s*:\s*([\d.]+)', msg)
                            if m:
                                try:
                                    transcript_delay = float(m.group(1))
                                except (ValueError, AttributeError):
                                    pass

                    # Rufe Metriken-Handler auf wenn Transkript vorhanden ist
                    if transcript_text:
                        try:
                            on_user_transcript(transcript_text, transcript_delay=transcript_delay)
                        except Exception as e:
                            logger.debug(f"[TRANSCRIPT-HANDLER-ERROR] {str(e)[:100]}")
                except Exception:
                    # Fehler nicht propagieren
                    pass

        # Registriere Handler für LiveKit Logs
        livekit_transcript_handler = LivekitTranscriptHandler()
        livekit_logger = logging.getLogger('livekit.agents')
        livekit_logger.addHandler(livekit_transcript_handler)

        # === SESSION CLEANUP HANDLER ===
        def remove_livekit_handler(*args, **kwargs):
            """Entferne Handler beim Session-Ende"""
            try:
                livekit_logger.removeHandler(livekit_transcript_handler)
            except Exception:
                pass

        def mark_session_closed(*args, **kwargs):
            """Markiere Session als beendet und räume auf"""
            setattr(session, 'closed', True)
            remove_livekit_handler()

        # Registriere Cleanup-Callback für Session-Ende
        if hasattr(session, 'on_closed') and callable(getattr(session, 'on_closed')):
            session.on_closed(mark_session_closed)


        # Hilfsfunktion für Summary-Logging
        def log_summary(summary, fallback=False):
            nonlocal summary_written

            # Persist to JSON file
            try:
                with open(metrics_json, 'w', encoding='utf-8') as jf:
                    json.dump(summary, jf, ensure_ascii=False, indent=2)
                logger.debug(f"[EVAL] Summary written to {metrics_json}")
            except Exception as e:
                logger.debug(f"Failed to write summary JSON: {e}")

            # Console logging
            logger.info("="*80)
            logger.info("FALLBACK METRIC SUMMARY" if fallback else "CALL BEENDET - FINALE METRIKEN")
            logger.info("="*80)
            logger.info(f"Call-ID: {summary.get('call_id')}")
            logger.info(f"Room: {summary.get('room')}")
            logger.info(f"Start: {summary.get('start_time')}")
            logger.info(f"Ende: {summary.get('end_time')}")
            logger.info(f"Gesamtdauer: {summary.get('duration_sec')}s")
            logger.info(f"Teilnehmer: {summary.get('participants') or '[]'}")
            logger.info(f"Anzahl Turns: {summary.get('turns')}")
            logger.info(f"STT-Timeouts: {summary.get('stt_timeouts')}")
            logger.info("-"*80)

            # Agent-Startup Latenz (Zeit bis Begrüßung gesendet)
            startup_lat = summary.get('agent_startup_latency')
            logger.info(f"Agent-Startup-Latenz: {f'{startup_lat:.3f}s' if startup_lat else 'N/A'}")
            logger.info("-"*80)

            for metric, label in [('avg_stt_latency', 'STT'), ('avg_llm_latency', 'LLM'), ('avg_tts_latency', 'TTS')]:
                val = summary.get(metric)
                logger.info(f"Durchschn. {label}-Latenz: {f'{val:.3f}s' if val else 'N/A'}")

            logger.info(f"Gesamt TTS-Bytes: {summary.get('total_tts_bytes')}")
            logger.info(f"Gesamt TTS-Sekunden: {summary.get('total_tts_seconds')}")
            logger.info("-"*80)

            # EOU details
            eou = summary.get('eou_metrics', [])
            logger.info(f"EINZELNE TURNS (Gesamt: {len(eou)})")
            for ev in eou:
                metrics_str = ", ".join([
                    f"{k.upper().replace('_LATENCY','')}={f'{v:.3f}s' if v else 'N/A'}"
                    for k, v in [('stt_latency', ev.get('stt_latency')),
                                 ('llm_latency', ev.get('llm_latency')),
                                 ('tts_latency', ev.get('tts_latency'))]
                ])
                logger.info(f"  Turn {ev.get('turn')}: {metrics_str}")
                logger.info(f"    Text: '{ev.get('transcript')}'")

            logger.info("-"*80)

            # LLM tokens if available
            llm_calls = summary.get('llm_calls', [])
            if llm_calls:
                total_in = sum((x.get('tokens_in') or 0) for x in llm_calls)
                total_out = sum((x.get('tokens_out') or 0) for x in llm_calls)
                logger.info(f"LLM: {len(llm_calls)} Calls, {total_in} Input-Tokens, {total_out} Output-Tokens")
                logger.info("-"*80)

            logger.info(f"Disconnect: {summary.get('disconnect_reason')} um {summary.get('disconnect_time')}")
            logger.info("="*80)

            # JSON debug log
            logger.debug(f"[METRIC-SUMMARY-JSON] {json.dumps(summary, ensure_ascii=False, indent=2)}")
            summary_written = True

        # Warte auf Session-Ende und logge Metriken
        try:
            while not getattr(session, 'closed', False):
                await asyncio.sleep(0.5)

            summary = usage_collector.summarize()
            log_summary(summary)
        except Exception as e:
            logger.error(f"Fehler beim Logging der Metriken: {e}")

    except Exception as e:
        logger.error(f"Fehler in entrypoint: {e}", exc_info=True)
        raise
    finally:
        # Fallback: Falls Summary noch nicht geschrieben
        if not summary_written:
            try:
                summary = usage_collector.summarize()
                summary['note'] = 'fallback_summary'
                log_summary(summary, fallback=True)
            except Exception as e:
                logger.error(f"Fehler beim Erstellen der Fallback-Summary: {e}")


def main():
    """Hauptfunktion"""
    # Umgebungsvariablen wurden bereits im __main__ Block geladen und validiert
    # Debug: Zeige kritische Variablen
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    logger.info(f"🔍 LIVEKIT_URL: {livekit_url}")
    logger.info(f"🔍 LIVEKIT_API_KEY: {livekit_api_key}")
    logger.info(f"🔍 LIVEKIT_API_SECRET: {'***' if livekit_api_secret else 'NOT SET'}")
    logger.info(f"🔍 OPENAI_API_KEY Länge: {len(api_key)} Zeichen")

    # Validiere kritische Variablen
    if not livekit_api_key or not livekit_api_secret:
        logger.error("❌ LIVEKIT_API_KEY oder LIVEKIT_API_SECRET nicht gesetzt!")
        return

    logger.info("✅ Alle Credentials validiert")
    logger.info("🚀 Starte Voice Agent Worker mit cli.run_app()...")


    # Starte Worker mit Prewarm
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )


if __name__ == "__main__":
    # Wichtig für Windows multiprocessing
    import multiprocessing
    multiprocessing.freeze_support()

    # Lade .env.local mit override=True um ALLE Variablen zu setzen
    env_path = Path(__file__).parent.parent / ".env.local"
    load_dotenv(dotenv_path=str(env_path), override=True, verbose=False)

    # WICHTIG: Verifiziere dass alle kritischen Variablen gesetzt sind
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    logger.info(f"✅ LIVEKIT_URL: {livekit_url}")
    logger.info(f"✅ LIVEKIT_API_KEY: {livekit_api_key}")
    logger.info(f"✅ LIVEKIT_API_SECRET: {'***' if livekit_api_secret else 'NOT SET'}")
    logger.info(f"✅ OPENAI_API_KEY geladen: {len(api_key)} Zeichen")

    # Validiere kritische Variablen
    if not livekit_url:
        logger.error("❌ LIVEKIT_URL not set!")
        import sys
        sys.exit(1)

    if not livekit_api_key:
        logger.error("❌ LIVEKIT_API_KEY not set!")
        import sys
        sys.exit(1)

    if not livekit_api_secret:
        logger.error("❌ LIVEKIT_API_SECRET not set!")
        import sys
        sys.exit(1)

    if not api_key or not api_key.startswith("sk-"):
        logger.error(f"❌ OPENAI_API_KEY nicht gesetzt oder ungültig")
        import sys
        sys.exit(1)

    logger.info("✅ Alle Umgebungsvariablen validiert!")
    main()
