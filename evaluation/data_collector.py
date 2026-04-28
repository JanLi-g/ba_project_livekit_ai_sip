#!/usr/bin/env python3
"""
Real-Time Test Data Collector
Sammelt Metriken während Web-UI und SIP Tests durchgeführt werden
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import re


class TestDataCollector:
    """Sammelt Metriken für Web-UI und SIP Calls"""

    def __init__(self, test_type: str = "webui", results_dir: str = "evaluation/results"):
        """
        Args:
            test_type: "webui" oder "sip"
            results_dir: Verzeichnis für Ergebnisse
        """
        self.test_type = test_type
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # CSV für diese Test-Serie
        self.csv_file = self.results_dir / f"{test_type}_calls.csv"
        self.calls = []
        self.call_counter = 0

        # CSV Headers definieren
        if test_type == "webui":
            self.headers = [
                "call_id", "category", "prompt", "start_time",
                "e2e_latency_ms", "network_latency_ms", "buffering_latency_ms",
                "stt_latency_ms", "llm_latency_ms", "tts_latency_ms",
                "mos", "intelligibility", "naturalness", "overall",
                "artifacts_type", "jitter_ms", "packet_loss_percent", "bitrate_kbps",
                "cpu_percent", "ram_mb", "cpu_agent_percent", "ram_agent_mb",
                "stt_tokens", "llm_input_tokens", "llm_output_tokens",
                "tts_characters", "api_cost_usd",
                "notes"
            ]
        else:  # sip
            self.headers = [
                "call_id", "timestamp", "prompt",
                "invite_received", "room_created", "agent_connected",
                "audio_downlink_ok", "mos", "intelligibility",
                "artifacts_type", "jitter_ms", "packet_loss_percent",
                "duration_sec", "error_type", "error_description", "notes"
            ]

        print(f"\n{'='*60}")
        print(f"Test Data Collector initialisiert: {test_type.upper()}")
        print(f"CSV: {self.csv_file}")
        print(f"{'='*60}\n")

    # ==================== WEB-UI CALLS ====================

    def start_webui_call(self, category: str, prompt: str) -> str:
        """
        Startet einen Web-UI Call

        Args:
            category: "short" | "medium" | "long"
            prompt: Der gesprochene Prompt-Text

        Returns:
            call_id für diesen Call
        """
        self.call_counter += 1
        call_id = f"{self.call_counter:03d}"

        start_time = datetime.now().isoformat()

        print(f"\n[WEB-UI CALL {call_id}] ({category.upper()})")
        print(f"Start: {start_time}")
        print(f"Prompt: {prompt}")
        print(f"→ Bitte sprechen und Agent-Antwort abhören...")

        return call_id

    def end_webui_call(
        self,
        call_id: str,
        category: str,
        prompt: str,
        e2e_latency: float,
        component_latencies: Optional[Dict] = None,
        mos: int = 3,
        audio_quality: Optional[Dict] = None,
        artifacts: str = "none",
        network_metrics: Optional[Dict] = None,
        resources: Optional[Dict] = None,
        api_usage: Optional[Dict] = None,
        notes: str = ""
    ):
        """
        Beendet einen Web-UI Call mit Metriken

        Args:
            call_id: Von start_webui_call()
            category: "short" | "medium" | "long"
            prompt: Der gesprochene Prompt
            e2e_latency: End-to-End Latenz in ms
            component_latencies: {network, buffering, stt, llm, tts} in ms
            mos: Mean Opinion Score (1-5)
            audio_quality: {intelligibility, naturalness, overall} (1-5)
            artifacts: "none" | "noise" | "delay" | "dropout" | ...
            network_metrics: {jitter_ms, packet_loss_percent, bitrate_kbps}
            resources: {cpu_percent, ram_mb, agent_cpu, agent_ram}
            api_usage: {stt_tokens, llm_input, llm_output, tts_chars, cost}
            notes: Beliebige Notizen
        """
        # Defaults
        component_latencies = component_latencies or {}
        audio_quality = audio_quality or {}
        network_metrics = network_metrics or {}
        resources = resources or {}
        api_usage = api_usage or {}

        # Messdaten vorbereiten
        call_data = {
            "call_id": call_id,
            "category": category,
            "prompt": prompt,
            "start_time": datetime.now().isoformat(),
            "e2e_latency_ms": e2e_latency,
            "network_latency_ms": component_latencies.get("network", 0),
            "buffering_latency_ms": component_latencies.get("buffering", 0),
            "stt_latency_ms": component_latencies.get("stt", 0),
            "llm_latency_ms": component_latencies.get("llm", 0),
            "tts_latency_ms": component_latencies.get("tts", 0),
            "mos": mos,
            "intelligibility": audio_quality.get("intelligibility", mos),
            "naturalness": audio_quality.get("naturalness", mos),
            "overall": audio_quality.get("overall", mos),
            "artifacts_type": artifacts,
            "jitter_ms": network_metrics.get("jitter_ms", 0),
            "packet_loss_percent": network_metrics.get("packet_loss_percent", 0),
            "bitrate_kbps": network_metrics.get("bitrate_kbps", 0),
            "cpu_percent": resources.get("cpu_percent", 0),
            "ram_mb": resources.get("ram_mb", 0),
            "cpu_agent_percent": resources.get("agent_cpu_percent", 0),
            "ram_agent_mb": resources.get("agent_ram_mb", 0),
            "stt_tokens": api_usage.get("stt_tokens", 0),
            "llm_input_tokens": api_usage.get("llm_input_tokens", 0),
            "llm_output_tokens": api_usage.get("llm_output_tokens", 0),
            "tts_characters": api_usage.get("tts_characters", 0),
            "api_cost_usd": api_usage.get("cost_usd", 0),
            "notes": notes
        }

        self.calls.append(call_data)

        # Ausgabe
        print(f"✓ CALL BEENDET")
        print(f"  E2E Latenz: {e2e_latency:.0f} ms")
        print(f"  MOS: {mos}/5")
        print(f"  Artefakte: {artifacts}")
        print(f"  CPU: {resources.get('cpu_percent', 'N/A')}%")
        print(f"  Kosten: ${api_usage.get('cost_usd', 0):.4f}")

        self._save_to_csv(call_data)

    # ==================== SIP CALLS ====================

    def start_sip_call(self, prompt: str) -> str:
        """
        Startet einen SIP Call

        Returns:
            call_id für diesen Call
        """
        self.call_counter += 1
        call_id = f"{self.call_counter:03d}"

        timestamp = datetime.now().isoformat()

        print(f"\n[SIP CALL {call_id}]")
        print(f"Timestamp: {timestamp}")
        print(f"Prompt: {prompt}")
        print(f"→ Jetzt Smartphone anrufen +49XXXXXXX")

        return call_id

    def end_sip_call(
        self,
        call_id: str,
        prompt: str,
        signaling_status: Dict,  # {invite: bool, room: bool, agent: bool}
        audio_downlink_ok: bool,
        mos: Optional[int] = None,
        audio_quality: Optional[Dict] = None,
        artifacts: str = "none",
        network_metrics: Optional[Dict] = None,
        duration_sec: float = 0,
        error_type: str = "",
        error_description: str = "",
        notes: str = ""
    ):
        """
        Beendet einen SIP Call

        Args:
            call_id: Von start_sip_call()
            prompt: Der gesprochene Prompt
            signaling_status: {invite: bool, room: bool, agent: bool}
            audio_downlink_ok: Ob Agent hörbar war
            mos: (optional) MOS wenn Audio hörbar
            audio_quality: {intelligibility, naturalness}
            artifacts: "none" | "noise" | "delay" | ...
            network_metrics: {jitter_ms, packet_loss_percent}
            duration_sec: Call-Dauer
            error_type: z.B. "RTP_TIMEOUT" | "CODEC_MISMATCH" | ""
            error_description: Detaillierte Fehlerbeschreibung
            notes: Weitere Notizen
        """
        audio_quality = audio_quality or {}
        network_metrics = network_metrics or {}

        call_data = {
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "invite_received": signaling_status.get("invite", False),
            "room_created": signaling_status.get("room", False),
            "agent_connected": signaling_status.get("agent", False),
            "audio_downlink_ok": audio_downlink_ok,
            "mos": mos if audio_downlink_ok else None,
            "intelligibility": audio_quality.get("intelligibility", mos) if audio_downlink_ok else None,
            "artifacts_type": artifacts,
            "jitter_ms": network_metrics.get("jitter_ms", 0),
            "packet_loss_percent": network_metrics.get("packet_loss_percent", 0),
            "duration_sec": duration_sec,
            "error_type": error_type,
            "error_description": error_description,
            "notes": notes
        }

        self.calls.append(call_data)

        # Ausgabe
        invite_ok = "✓" if signaling_status.get("invite") else "✗"
        room_ok = "✓" if signaling_status.get("room") else "✗"
        agent_ok = "✓" if signaling_status.get("agent") else "✗"
        audio_ok = "✓" if audio_downlink_ok else "✗"

        print(f"✓ CALL BEENDET")
        print(f"  Signalisierung: INVITE {invite_ok} | Room {room_ok} | Agent {agent_ok}")
        print(f"  Audio: {audio_ok} {'(MOS: '+str(mos)+'/5)' if audio_downlink_ok else ''}")
        if error_type:
            print(f"  ⚠️ Fehler: {error_type} – {error_description}")

        self._save_to_csv(call_data)

    # ==================== UTILITIES ====================

    def _save_to_csv(self, call_data: Dict):
        """Speichert einen Call in die CSV-Datei"""
        # Initialisiere CSV wenn leer
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

        # Append
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            # Nur relevante Spalten speichern
            filtered_data = {k: call_data.get(k, '') for k in self.headers}
            writer.writerow(filtered_data)

    def extract_agent_logs(self, log_file: str, call_id: str) -> Dict:
        """
        Extrahiert Latenzen aus Agent-Worker Logs

        Args:
            log_file: Pfad zu agent_worker.log
            call_id: Call-ID zum Filtern

        Returns:
            Dict mit {e2e_latency, components: {network, stt, llm, tts}}
        """
        try:
            with open(log_file, 'r') as f:
                logs = f.readlines()

            # Beispiel: Log-Parser
            # [DEBUG] Call-001 | STT-Start: 1000, STT-End: 1230
            # [DEBUG] Call-001 | LLM-Start: 1230, LLM-End: 1710

            # Hier könnte komplexere Parsing-Logik stehen
            # Für jetzt: Mock-Rückgabe
            return {
                "e2e_latency": 1000,
                "components": {
                    "network": 75,
                    "buffering": 120,
                    "stt": 230,
                    "llm": 480,
                    "tts": 95
                }
            }
        except FileNotFoundError:
            print(f"⚠️  Log-Datei nicht gefunden: {log_file}")
            return {}

    def extract_docker_stats(self) -> Dict:
        """
        Ruft aktuelle Docker-Stats ab

        Returns:
            Dict mit {cpu_percent, ram_mb, ...}
        """
        try:
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format",
                 "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse output: livekit-sip | 3% | 55MB / 16GB
            stats = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    name = parts[0].replace('/', '')
                    cpu = float(parts[1].rstrip('%'))
                    mem = parts[2].split('/')[0].strip()
                    stats[name] = {"cpu": cpu, "mem": mem}

            return stats
        except Exception as e:
            print(f"⚠️  Docker-Stats Fehler: {e}")
            return {}

    def summary_report(self) -> str:
        """Erzeugt eine Zusammenfassung der durchgeführten Tests"""
        if not self.calls:
            return "Keine Calls durchgeführt."

        from statistics import mean, stdev

        # Web-UI spezifisch
        if self.test_type == "webui":
            latencies = [c["e2e_latency_ms"] for c in self.calls if c.get("e2e_latency_ms")]
            mos_scores = [c["mos"] for c in self.calls if c.get("mos")]

            report = f"""
{'='*60}
WEB-UI TEST SUMMARY
{'='*60}
Total Calls:           {len(self.calls)}
Latenz (μ):            {mean(latencies):.0f} ms
Latenz (σ):            {stdev(latencies):.0f} ms (wenn N > 1)
Latenz Range:          {min(latencies):.0f}–{max(latencies):.0f} ms
MOS (avg):             {mean(mos_scores):.2f}
MOS ≥ 4:               {sum(1 for m in mos_scores if m >= 4)}/{len(mos_scores)} ({sum(1 for m in mos_scores if m >= 4)/len(mos_scores)*100:.1f}%)
CSV Export:            {self.csv_file}
"""

        # SIP spezifisch
        else:  # sip
            success_count = sum(1 for c in self.calls if c.get("audio_downlink_ok"))
            mos_scores = [c["mos"] for c in self.calls if c.get("mos")]

            report = f"""
{'='*60}
SIP TEST SUMMARY
{'='*60}
Total Calls:           {len(self.calls)}
Audio Downlink OK:     {success_count}/{len(self.calls)} ({success_count/len(self.calls)*100:.1f}%)
MOS (avg, successful): {mean(mos_scores) if mos_scores else 'N/A'}
CSV Export:            {self.csv_file}
"""

        return report

    def finalize(self):
        """Finalisiert die Test-Session"""
        print(self.summary_report())
        print(f"✓ Alle Daten exportiert: {self.csv_file}")


# ==================== BEISPIELVERWENDUNG ====================

if __name__ == "__main__":
    import sys

    # Argument: "webui" oder "sip"
    test_type = sys.argv[1] if len(sys.argv) > 1 else "webui"

    collector = TestDataCollector(test_type=test_type)

    # Beispiel Web-UI Call
    if test_type == "webui":
        call_id = collector.start_webui_call("short", "Wie ist das Wetter?")
        time.sleep(2)  # Simulation

        collector.end_webui_call(
            call_id=call_id,
            category="short",
            prompt="Wie ist das Wetter?",
            e2e_latency=920,
            component_latencies={
                "network": 75,
                "buffering": 120,
                "stt": 230,
                "llm": 480,
                "tts": 95
            },
            mos=5,
            audio_quality={"intelligibility": 5, "naturalness": 5, "overall": 5},
            artifacts="none",
            network_metrics={"jitter_ms": 12, "packet_loss_percent": 0.3, "bitrate_kbps": 48},
            resources={"cpu_percent": 28, "ram_mb": 580, "agent_cpu_percent": 18, "agent_ram_mb": 320},
            api_usage={"stt_tokens": 15, "llm_input_tokens": 20, "llm_output_tokens": 25, "tts_characters": 80, "cost_usd": 0.0015},
            notes="Clear audio, natural response"
        )

    # Beispiel SIP Call
    else:
        call_id = collector.start_sip_call("Wie ist das Wetter?")
        time.sleep(3)  # Simulation

        collector.end_sip_call(
            call_id=call_id,
            prompt="Wie ist das Wetter?",
            signaling_status={"invite": True, "room": True, "agent": True},
            audio_downlink_ok=True,
            mos=4,
            audio_quality={"intelligibility": 4, "naturalness": 4},
            artifacts="none",
            network_metrics={"jitter_ms": 25, "packet_loss_percent": 0.5},
            duration_sec=45,
            notes="Good quality, slight delay"
        )

    collector.finalize()

