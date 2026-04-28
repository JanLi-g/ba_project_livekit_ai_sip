#!/usr/bin/env python3
"""
Analysiere genau 30 WebUI Calls: 10 kurz + 15 mittel + 5 lang
"""
import csv, json, statistics as stats
from pathlib import Path

CSV_PATH = Path('evaluation/results/webui_calls_enriched.csv')
if not CSV_PATH.exists():
    CSV_PATH = Path('evaluation/results/webui_calls.csv')

OUT_DIR = Path('evaluation/results')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Lese alle Calls
all_calls = []
with CSV_PATH.open('r', encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        all_calls.append(row)

# Filtere nach Kategorie: 10 short + 15 medium + 5 long
short_calls = [c for c in all_calls if c.get('category') == 'short'][:10]
medium_calls = [c for c in all_calls if c.get('category') == 'medium'][:15]
long_calls = [c for c in all_calls if c.get('category') == 'long'][:5]

calls = short_calls + medium_calls + long_calls
print(f"📊 Gefiltert: {len(short_calls)} kurz + {len(medium_calls)} mittel + {len(long_calls)} lang = {len(calls)} Total")

def to_float(x):
    try:
        return float(x) if x else None
    except Exception:
        return None

# Sammle Metriken
transcript_delays = [to_float(c.get('transcript_delay_ms','')) for c in calls]
cpu = [to_float(c.get('cpu_percent','')) for c in calls]
ram = [to_float(c.get('ram_mb','')) for c in calls]

# Filter: nur Werte, die nicht None sind und > 0
transcript_delays = [x for x in transcript_delays if x is not None and x > 0]
cpu = [x for x in cpu if x is not None and x > 0]
ram = [x for x in ram if x is not None and x > 0]

print(f"✅ transcript_delay_ms Samples: {len(transcript_delays)}")
print(f"✅ CPU Samples: {len(cpu)}")
print(f"✅ RAM Samples: {len(ram)}")

summary = {
    'metadata': {
        'total_calls': len(calls),
        'short_calls': len(short_calls),
        'medium_calls': len(medium_calls),
        'long_calls': len(long_calls),
        'source': CSV_PATH.name,
    },
    'stt_latency_ms': {
        'metric': 'Speech-to-Text Latenz (OpenAI Whisper)',
        'count': len(transcript_delays),
        'mean': round(stats.mean(transcript_delays), 2) if transcript_delays else None,
        'median': round(stats.median(transcript_delays), 2) if transcript_delays else None,
        'stdev': round(stats.pstdev(transcript_delays), 2) if len(transcript_delays) > 1 else None,
        'min': min(transcript_delays) if transcript_delays else None,
        'max': max(transcript_delays) if transcript_delays else None,
    },
    'resources': {
        'cpu_percent': {
            'mean': round(stats.mean(cpu), 1) if cpu else None,
            'max': max(cpu) if cpu else None,
        },
        'ram_mb': {
            'mean': round(stats.mean(ram), 0) if ram else None,
            'max': max(ram) if ram else None,
        }
    }
}

with (OUT_DIR/'webui_summary_30calls.json').open('w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

with (OUT_DIR/'SUMMARY_REPORT_30CALLS.md').open('w', encoding='utf-8') as f:
    f.write('# WebUI Evaluation – 30 Calls (Kurz/Mittel/Lang)\n\n')
    f.write(f"**Calls gesamt:** {summary['metadata']['total_calls']}\n")
    f.write(f"- Kurz (1–5 Sek): {summary['metadata']['short_calls']}\n")
    f.write(f"- Mittel (5–15 Sek): {summary['metadata']['medium_calls']}\n")
    f.write(f"- Lang (15+ Sek): {summary['metadata']['long_calls']}\n\n")
    f.write(f"**Quelle:** {summary['metadata']['source']}\n\n")
    f.write('## Speech-to-Text Latenz (OpenAI Whisper)\n\n')
    f.write(f"- **Durchschnitt:** {summary['stt_latency_ms']['mean']} ms\n")
    f.write(f"- **Median:** {summary['stt_latency_ms']['median']} ms\n")
    f.write(f"- **Min/Max:** {summary['stt_latency_ms']['min']}–{summary['stt_latency_ms']['max']} ms\n")
    f.write(f"- **Std.abw.:** {summary['stt_latency_ms']['stdev']} ms\n")
    f.write(f"- **Samples:** {summary['stt_latency_ms']['count']}\n\n")
    f.write('## Systemressourcen\n\n')
    f.write(f"- **CPU:** Ø {summary['resources']['cpu_percent']['mean']}%, Max {summary['resources']['cpu_percent']['max']}%\n")
    f.write(f"- **RAM:** Ø {summary['resources']['ram_mb']['mean']} MB, Max {summary['resources']['ram_mb']['max']} MB\n")

print(f"✅ Report geschrieben: evaluation/results/SUMMARY_REPORT_30CALLS.md")
print(f"✅ JSON gespeichert: evaluation/results/webui_summary_30calls.json")

