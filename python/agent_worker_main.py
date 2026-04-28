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
        self.disconnect_reason = None
        self.disconnect_participant = None
        self.disconnect_time = None

    def add_participant(self, participant_id: str):
        if participant_id:
            self.participants.add(str(participant_id))

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
            'total_tts_bytes': sum((x.get('audio_bytes') or 0) for x in self.tts_calls),
            'total_tts_seconds': sum((x.get('audio_seconds') or 0) for x in self.tts_calls),
            'eou_metrics': self.eou_metrics,
            'llm_calls': self.llm_calls,
            'tts_calls': self.tts_calls,
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
        logger.info("⚡ Verbinde mit Room und starte Session...")

        await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
        logger.info("✅ Room verbunden!")

        # --- Evaluation/Turn-Metriken ---
        metrics_dir = Path.cwd() / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Metrics directory ready at: {metrics_dir}")

        metrics_ndjson = metrics_dir / f"{call_id}.ndjson"
        metrics_json = metrics_dir / f"{call_id}.json"

        # Turn-Tracking Variablen
        turn_counter = 0
        last_turn_time = time.perf_counter()
        pending_turn_data = {
            'stt_latency': 0.0,
            'llm_latency': 0.0,
            'tts_latency': 0.0,
            'transcript': None,
            'transcript_delay': None
        }

        logger.info("🤖 Erstelle Agent...")

        # Usage collector für strukturierte Metriken
        usage_collector = UsageCollector(call_id=call_id, room=room_name)

        # --- EVENT-LISTENER REGISTRATION ---
        @ctx.room.on("participant_connected")
        def on_participant_joined(participant):
            if participant:
                usage_collector.add_participant(participant_id=participant.identity)
                logger.info(f"[LIVEKIT] participant_connected: participant={participant.identity} time={time.strftime('%Y-%m-%d %H:%M:%S')}")

        @ctx.room.on("participant_disconnected")
        def on_participant_disconnected(participant):
            participant_id = participant.identity if participant else None
            logger.info(f"[LIVEKIT] participant_disconnected: participant={participant_id} reason=CLIENT_INITIATED time={time.strftime('%Y-%m-%d %H:%M:%S')}")
            usage_collector.record_disconnect(reason="CLIENT_INITIATED", participant=participant_id)
            setattr(session, 'closed', True)

        # --- METRICS RECORDING FUNCTION ---
        def on_user_transcript(transcript: str, transcript_delay: float = None):
            """Erfasse und logge Turn-Metriken"""
            nonlocal turn_counter, last_turn_time, pending_turn_data, metrics_logging_enabled
            if not metrics_logging_enabled:
                return

            turn_counter += 1
            now = time.perf_counter()
            turn_duration = now - last_turn_time
            last_turn_time = now

            stt_lat = pending_turn_data.get('stt_latency', 0.0) or 0.0
            llm_lat = pending_turn_data.get('llm_latency', 0.0) or 0.0
            tts_lat = pending_turn_data.get('tts_latency', 0.0) or 0.0

            # Live-Metrik-Logging
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

            # Persist turn als NDJSON
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

            # Setze die Latenzen zurück
            pending_turn_data['stt_latency'] = 0.0
            pending_turn_data['llm_latency'] = 0.0
            pending_turn_data['tts_latency'] = 0.0
            pending_turn_data['transcript'] = None
            pending_turn_data['transcript_delay'] = None

        # Erstelle und starte Session
        session = AgentSession()

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

        # Sende Begrüßung
        await asyncio.sleep(1)
        logger.info("🗣️ Sende Begrüßung...")
        await session.say(greeting, allow_interruptions=True)
        logger.info("✅ Begrüßung gesendet")


        # Patche STT für Timeout-Tracking und Latenz
        orig_stt = agent.stt
        if hasattr(orig_stt, 'recognize'):
            orig_recognize = orig_stt.recognize
            async def recognize_with_timeout_count(*args, **kwargs):
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

        # Patche LLM für Latenz und Token-Tracking
        orig_llm = agent.llm

        # Versuche mehrere mögliche LLM-Methoden zu patchen
        # Die OpenAI LLM nutzt intern chat.completions.create() via einen agentic_loop

        # Patch 1: Versuche chat() oder agentic_loop_call()
        for method_name in ['chat', 'agentic_loop_call', '__call__']:
            if hasattr(orig_llm, method_name):
                orig_method = getattr(orig_llm, method_name)

                async def create_llm_wrapper(orig_fn, method_name_inner):
                    async def llm_call_with_latency(*args, **kwargs):
                        nonlocal pending_turn_data
                        start = time.perf_counter()
                        try:
                            result = await orig_fn(*args, **kwargs)
                        except Exception as e:
                            # Auch bei Fehler die Latenz messen
                            llm_latency = time.perf_counter() - start
                            pending_turn_data['llm_latency'] = llm_latency
                            usage_collector.record_llm(latency=llm_latency, model=getattr(orig_llm, 'model', None))
                            logger.debug(f"[LLM-PATCH] latency={llm_latency:.3f}s (error: {type(e).__name__})")
                            raise

                        llm_latency = time.perf_counter() - start
                        pending_turn_data['llm_latency'] = llm_latency

                        # Extrahiere Token-Usage
                        tokens_in, tokens_out = None, None
                        try:
                            # Versuche verschiedene Strukturen für usage
                            usage = None
                            if isinstance(result, dict):
                                usage = result.get('usage')
                            else:
                                usage = getattr(result, 'usage', None)

                            if usage:
                                if isinstance(usage, dict):
                                    tokens_in = usage.get('prompt_tokens') or usage.get('input_tokens')
                                    tokens_out = usage.get('completion_tokens') or usage.get('output_tokens')
                                else:
                                    tokens_in = getattr(usage, 'prompt_tokens', None) or getattr(usage, 'input_tokens', None)
                                    tokens_out = getattr(usage, 'completion_tokens', None) or getattr(usage, 'output_tokens', None)
                        except Exception as e:
                            logger.debug(f"[LLM-PATCH] Could not extract tokens: {e}")

                        model_name = getattr(orig_llm, 'model', None)
                        usage_collector.record_llm(latency=llm_latency, model=model_name, tokens_in=tokens_in, tokens_out=tokens_out)
                        logger.debug(f"[LLM-PATCH] {method_name_inner} latency={llm_latency:.3f}s, tokens_in={tokens_in}, tokens_out={tokens_out}")
                        return result
                    return llm_call_with_latency

                # Setze die gepatchte Methode
                if callable(orig_method):
                    setattr(orig_llm, method_name, create_llm_wrapper(orig_method, method_name))

        # Patche TTS für Latenz (als async Kontextmanager)
        orig_tts = agent.tts
        if hasattr(orig_tts, 'synthesize'):
            orig_synthesize = orig_tts.synthesize

            class AudioStreamWrapper:
                """Wrapper um TTS-Stream für Byte-Counting"""
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

                        # Extract bytes from SynthesizedAudio object or raw bytes
                        try:
                            if hasattr(chunk, 'frame'):
                                # SynthesizedAudio with .frame attribute (RTCAudioFrame)
                                frame = chunk.frame
                                if hasattr(frame, 'data'):
                                    self.bytes_count += len(frame.data)
                                    # Calculate audio duration from sample rate
                                    if hasattr(frame, 'sample_rate') and hasattr(frame, 'samples_per_channel'):
                                        self.audio_seconds += frame.samples_per_channel / frame.sample_rate
                            elif hasattr(chunk, 'data'):
                                # Direct data attribute
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
                """Kontextmanager für TTS mit Latenz-Messung"""
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

                        audio_bytes = getattr(self._entered, 'bytes_count', None) if self._entered else None
                        audio_seconds = getattr(self._entered, 'audio_seconds', None) if self._entered else None

                        # Filter out zero values
                        if audio_bytes is not None and audio_bytes == 0:
                            audio_bytes = None
                        if audio_seconds is not None and audio_seconds == 0.0:
                            audio_seconds = None

                        usage_collector.record_tts(latency=tts_latency, audio_bytes=audio_bytes, audio_seconds=audio_seconds)
                        logger.debug(f"[TTS-PATCH] latency={tts_latency:.3f}s, bytes={audio_bytes}, seconds={audio_seconds}")

            def synthesize_with_latency(*args, **kwargs):
                return SynthesizeWithLatency(*args, **kwargs)
            orig_tts.synthesize = synthesize_with_latency

        # Event-Listener für User-Transkripte (nur für Evaluation)
        metrics_logging_enabled = False

        def on_user_transcript(transcript, transcript_delay=None):
            """Erfasse Turn-Metrik synchron ohne async (wird über asyncio.create_task aufgerufen)"""
            nonlocal turn_counter, last_turn_time, pending_turn_data
            if not metrics_logging_enabled:
                return

            turn_counter += 1
            now = time.perf_counter()
            turn_duration = now - last_turn_time
            last_turn_time = now

            stt_lat = pending_turn_data.get('stt_latency', 0.0) or 0.0
            llm_lat = pending_turn_data.get('llm_latency', 0.0) or 0.0
            tts_lat = pending_turn_data.get('tts_latency', 0.0) or 0.0

            # Live-Metrik-Logging
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

            # Persist turn als NDJSON
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

            # Setze die Latenzen zurück
            pending_turn_data['stt_latency'] = 0.0
            pending_turn_data['llm_latency'] = 0.0
            pending_turn_data['tts_latency'] = 0.0
            pending_turn_data['transcript'] = None
            pending_turn_data['transcript_delay'] = None

        # Begrüßung wurde gesendet, Logging aktivieren
        metrics_logging_enabled = True
        logger.debug("[METRICS] Metrics logging enabled - transcripts will now be recorded")

        # Handler to capture 'received user transcript' from livekit.agents logger
        class LivekitTranscriptHandler(logging.Handler):
            def __init__(self):
                super().__init__()

            def emit(self, record):
                nonlocal metrics_logging_enabled
                if not metrics_logging_enabled:
                    return

                try:
                    msg = record.getMessage() if hasattr(record, 'getMessage') else str(record.msg)
                    if 'received user transcript' not in msg:
                        return

                    transcript_text = None
                    transcript_delay = None

                    # Versuche zuerst, aus record.__dict__ Attributen zu extrahieren
                    transcript_text = getattr(record, 'user_transcript', None)
                    transcript_delay = getattr(record, 'transcript_delay', None)

                    # Fallback: JSON-Extraktion aus Message
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

                    # Nur wenn transcript_text vorhanden ist
                    if transcript_text:
                        try:
                            on_user_transcript(transcript_text, transcript_delay=transcript_delay)
                        except Exception as e:
                            logger.debug(f"[TRANSCRIPT-HANDLER-ERROR] {str(e)[:100]}")
                except Exception as e:
                    # Fehler nicht propagieren
                    pass

        livekit_transcript_handler = LivekitTranscriptHandler()
        livekit_logger = logging.getLogger('livekit.agents')
        livekit_logger.addHandler(livekit_transcript_handler)

        # Setup cleanup for session close
        def remove_livekit_handler(*args, **kwargs):
            try:
                livekit_logger.removeHandler(livekit_transcript_handler)
            except Exception:
                pass

        def mark_session_closed(*args, **kwargs):
            setattr(session, 'closed', True)
            remove_livekit_handler()

        # Register session close callback
        if hasattr(session, 'on_closed') and callable(getattr(session, 'on_closed')):
            session.on_closed(mark_session_closed)

        # Aktiviere Metrics-Logging
        metrics_logging_enabled = True
        logger.debug("[METRICS] Metrics logging enabled - transcripts will now be recorded")
        logger.info("🎤 Agent läuft und wartet auf User Input")

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
    # Lade .env.local
    load_dotenv(".env.local")
    logger.info("✅ .env.local geladen")

    # Prüfe OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY nicht gesetzt in .env.local")
        return

    logger.info("✅ OpenAI API Key gefunden")
    logger.info("🚀 Starte Voice Agent Worker...")

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

    main()
