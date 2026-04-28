"""
Parse previously collected SIP status JSON/CSV and produce summary tables and a small report.
Reads: analysis/raw/sip_status.json or analysis/raw/sip_status.csv
Writes: analysis/processed/sip_status_summary.csv and analysis/processed/sip_status_report.txt
Also produces a simple boxplot of call durations if matplotlib is available.
"""
from __future__ import annotations
import os
import json
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BASE = os.path.dirname(__file__)
RAW = os.path.join(BASE, 'raw')
PROCESSED = os.path.join(BASE, 'processed')
os.makedirs(PROCESSED, exist_ok=True)


def load_data():
    json_path = os.path.join(RAW, 'sip_status.json')
    csv_path = os.path.join(RAW, 'sip_status.csv')

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    elif os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        items = payload.get('data', {}).get('sipCalls', [])
        df = pd.DataFrame(items)
    else:
        raise FileNotFoundError('Kein sip_status.json oder sip_status.csv in analysis/raw gefunden')

    # ensure durationSeconds numeric
    if 'durationSeconds' in df.columns:
        df['durationSeconds'] = pd.to_numeric(df['durationSeconds'], errors='coerce')
    else:
        df['durationSeconds'] = np.nan

    return df


def summarize(df: pd.DataFrame):
    n = len(df)
    durations = df['durationSeconds'].dropna()
    summary = {
        'n_calls': n,
        'n_with_duration': int(durations.notna().sum()),
        'mean_duration_s': float(durations.mean()) if not durations.empty else None,
        'median_duration_s': float(durations.median()) if not durations.empty else None,
        'std_duration_s': float(durations.std()) if not durations.empty else None,
        'min_duration_s': float(durations.min()) if not durations.empty else None,
        'max_duration_s': float(durations.max()) if not durations.empty else None,
        'iqr_s': float(durations.quantile(0.75) - durations.quantile(0.25)) if not durations.empty else None,
    }

    # Save CSV summary
    out_csv = os.path.join(PROCESSED, 'sip_status_summary.csv')
    pd.DataFrame([summary]).to_csv(out_csv, index=False)

    # Save human readable report
    out_txt = os.path.join(PROCESSED, 'sip_status_report.txt')
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write(f"SIP Status Report - generated: {datetime.utcnow().isoformat()}\n\n")
        for k, v in summary.items():
            f.write(f"{k}: {v}\n")

    print('Wrote', out_csv, 'and', out_txt)
    return summary


def plot_durations(df: pd.DataFrame):
    durations = df['durationSeconds'].dropna()
    if durations.empty:
        print('No durations to plot')
        return

    plt.figure(figsize=(6,3))
    plt.boxplot(durations, vert=False)
    plt.xlabel('Duration (s)')
    plt.title('Call duration distribution')
    out_png = os.path.join(PROCESSED, 'call_duration_boxplot.png')
    plt.savefig(out_png, bbox_inches='tight', dpi=150)
    plt.close()
    print('Wrote', out_png)


def main():
    df = load_data()
    summary = summarize(df)
    try:
        plot_durations(df)
    except Exception as e:
        print('Plotting failed (matplotlib missing?):', e)


if __name__ == '__main__':
    main()

