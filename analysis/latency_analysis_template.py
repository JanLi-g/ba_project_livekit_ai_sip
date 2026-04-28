"""
Template analysis script for latency / success rate once raw logs are available.
Assumes a CSV with columns: event_ts (ISO), session_id, event_type (e.g. 'stt_request', 'stt_response', 'tts_request', 'tts_response'), latency_ms, status
Writes summary CSV and simple plots.
"""
from __future__ import annotations
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

BASE = os.path.dirname(__file__)
RAW = os.path.join(BASE, 'raw')
PROCESSED = os.path.join(BASE, 'processed')
os.makedirs(PROCESSED, exist_ok=True)

LOG_CSV = os.path.join(RAW, 'events.csv')


def load_events():
    if not os.path.exists(LOG_CSV):
        raise FileNotFoundError(f'Kein events.csv in {RAW} gefunden. Erzeuge zuerst Rohdaten.')
    df = pd.read_csv(LOG_CSV, parse_dates=['event_ts'])
    return df


def summarize_latency(df: pd.DataFrame):
    # Filter latencies
    lat = df[df['latency_ms'].notna()]
    grp = lat.groupby('event_type')['latency_ms']
    summary = grp.agg(['count','median','mean','std','min','max'])
    out_csv = os.path.join(PROCESSED, 'latency_summary_by_event.csv')
    summary.to_csv(out_csv)
    print('Wrote', out_csv)
    return summary


def plot_latency(df: pd.DataFrame):
    lat = df[df['latency_ms'].notna()]
    if lat.empty:
        print('No latency entries found')
        return
    plt.figure(figsize=(8,4))
    df_box = [lat[lat.event_type==t].latency_ms for t in lat.event_type.unique()]
    labels = list(lat.event_type.unique())
    plt.boxplot(df_box, labels=labels, vert=False)
    plt.xlabel('Latency (ms)')
    plt.title('Latency by event type')
    out = os.path.join(PROCESSED, 'latency_boxplot.png')
    plt.savefig(out, bbox_inches='tight', dpi=150)
    plt.close()
    print('Wrote', out)


def main():
    df = load_events()
    summary = summarize_latency(df)
    plot_latency(df)


if __name__ == '__main__':
    main()

