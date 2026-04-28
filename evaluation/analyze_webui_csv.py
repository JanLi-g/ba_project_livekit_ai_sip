#!/usr/bin/env python3
import csv, json, statistics as stats
from pathlib import Path

# Nutze enriched CSV, falls vorhanden; sonst fallback auf original
CSV_PATH = Path('evaluation/results/webui_calls_enriched.csv')
if not CSV_PATH.exists():
    CSV_PATH = Path('evaluation/results/webui_calls.csv')

OUT_DIR = Path('evaluation/results')
OUT_DIR.mkdir(parents=True, exist_ok=True)

calls = []
with CSV_PATH.open('r', encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        calls.append(row)

print(f"📊 Analysiere {len(calls)} Calls aus {CSV_PATH.name}")

def to_float(x):
    try:
        return float(x) if x else None
    except Exception:
        return None

# Sammle Metriken
transcript_delays = [to_float(c.get('transcript_delay_ms','')) for c in calls]
cpu = [to_float(c.get('cpu_percent','')) for c in calls]
ram = [to_float(c.get('ram_mb','')) for c in calls]

# Filter: nur Werte, die nicht None sind
transcript_delays = [x for x in transcript_delays if x is not None and x > 0]
cpu = [x for x in cpu if x is not None and x > 0]
ram = [x for x in ram if x is not None and x > 0]

print(f"✅ transcript_delay_ms Samples: {len(transcript_delays)}")
print(f"✅ CPU Samples: {len(cpu)}")
print(f"✅ RAM Samples: {len(ram)}")

summary = {
    'metadata': {
        'total_calls': len(calls),
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

with (OUT_DIR/'webui_summary.json').open('w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)

with (OUT_DIR/'SUMMARY_REPORT.md').open('w', encoding='utf-8') as f:
    f.write('# WebUI Evaluation – Ergebnisse\n\n')
    f.write(f"**Calls gesamt:** {summary['metadata']['total_calls']}\n")
    f.write(f"**Quelle:** {summary['metadata']['source']}\n\n")
    f.write('## Speech-to-Text Latenz (Whisper API)\n')
    f.write(json.dumps(summary['stt_latency_ms'], indent=2))
    f.write('\n\n## Systemressourcen\n')
    f.write(json.dumps(summary['resources'], indent=2))

print(f"✅ Report geschrieben: evaluation/results/SUMMARY_REPORT.md")
print(f"✅ JSON gespeichert: evaluation/results/webui_summary.json")

print('✅ Ergebnisse gespeichert in evaluation/results/webui_summary.json und SUMMARY_REPORT.md')

