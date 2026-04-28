#!/usr/bin/env python3
"""
Merge Agent-Log-Metriken (transcript_delay) in die WebUI CSV.

Nutzung:
    python evaluation/merge_metrics.py \
        --csv evaluation/results/webui_calls.csv \
        --log evaluation/logs/agent_worker.log \
        --out evaluation/results/webui_calls_enriched.csv

Wenn --out weggelassen wird, wird die Original-CSV überschrieben.
"""

import argparse
import csv
import re
from pathlib import Path
from typing import List

TRANSCRIPT_PATTERNS = [
    r"transcript_delay\"\s*:\s*([0-9\.]+)",
    r"transcript_delay'\s*:\s*([0-9\.]+)",
    r"transcript_delay\s*[:=]\s*([0-9\.]+)",
]

FLOAT_ANY = re.compile(r"([0-9]+\.[0-9]+)")


def extract_delays_from_text(text: str) -> List[int]:
    values: List[int] = []

    # Strategie 1: Direkt nach "transcript_delay" mit Wert suchen (alle Varianten)
    for pat in TRANSCRIPT_PATTERNS:
        for match in re.finditer(pat, text):
            try:
                sec = float(match.group(1))
                ms = int(sec * 1000)
                if ms not in values:  # Duplikate vermeiden
                    values.append(ms)
            except Exception:
                pass

    # Strategie 2: Fallback für "received user transcript" Zeilen
    if not values:
        for line in text.splitlines():
            if "received user transcript" in line:
                floats = FLOAT_ANY.findall(line)
                if floats:
                    try:
                        sec = float(floats[-1])
                        ms = int(sec * 1000)
                        if ms not in values:
                            values.append(ms)
                    except Exception:
                        pass

    return values


def parse_transcript_delays_multi(log_path: Path) -> List[int]:
    # Primär: angegebene Datei
    delays: List[int] = []
    sources: List[Path] = []
    if log_path and log_path.exists():
        sources.append(log_path)
    # Fallback: weitere bekannte Dateien
    root = Path(__file__).resolve().parent.parent  # project root
    candidates = [
        root / "evaluation" / "logs" / "agent_transcript.log",
        root / "evaluation" / "logs" / "agent_worker.log",
        root / "livekit-logs.txt",
    ]
    for c in candidates:
        if c.exists() and c not in sources:
            sources.append(c)
    # Zusätzlich: alle Logs unter evaluation/logs
    logs_dir = root / "evaluation" / "logs"
    if logs_dir.exists():
        for p in logs_dir.glob("*.log"):
            if p not in sources:
                sources.append(p)
        for p in logs_dir.glob("*.txt"):
            if p not in sources:
                sources.append(p)
    # Aggregation
    for src in sources:
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            try:
                text = src.read_text(encoding="latin-1", errors="ignore")
            except Exception:
                continue
        vals = extract_delays_from_text(text)
        if vals:
            delays.extend(vals)
    return delays


def merge(csv_path: Path, log_path: Path, out_path: Path):
    if not csv_path.exists():
        print(f"❌ CSV nicht gefunden: {csv_path}")
        return

    delays_ms = parse_transcript_delays_multi(log_path)
    print(f"Gefundene transcript_delay-Werte (gesamt): {len(delays_ms)}")
    if delays_ms:
        print(f"Beispielwerte (ms): {delays_ms[:5]}")

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
        # Fieldnames robust bestimmen (Union aller Keys)
        fieldnames_set = set(reader.fieldnames or [])
        for r in rows:
            fieldnames_set.update(k for k in r.keys() if k is not None)
        fieldnames = list(fieldnames_set)

    # Neues Feld anhängen
    if "transcript_delay_ms" not in fieldnames:
        fieldnames.append("transcript_delay_ms")

    # Mappen nach Reihenfolge (first N delays mapped to first N rows)
    for idx, row in enumerate(rows):
        row.pop(None, None)
        row["transcript_delay_ms"] = str(delays_ms[idx]) if idx < len(delays_ms) else ""

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Geschrieben: {out_path} (Rows: {len(rows)})")


def main():
    parser = argparse.ArgumentParser(description="Merge transcript_delay aus Logs in CSV")
    parser.add_argument("--csv", default="evaluation/results/webui_calls.csv", help="Pfad zur CSV")
    parser.add_argument("--log", default="evaluation/logs/agent_worker.log", help="Primärer Log-Pfad (optional)")
    parser.add_argument("--out", default=None, help="Output-CSV (Standard: Original überschreiben)")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    log_path = Path(args.log) if args.log else None
    out_path = Path(args.out) if args.out else csv_path

    merge(csv_path, log_path, out_path)


if __name__ == "__main__":
    main()

