"""
Collect data from the local Next.js API endpoints and save raw JSON/CSV.
Usage:
  python analysis/collect_from_api.py --base-url http://localhost:3000

What it does:
 - GET /api/sip/status -> saves analysis/raw/sip_status.json and sip_status.csv
 - (Optional) POST to test endpoints if configured (not enabled by default)

This is a lightweight helper to quickly gather quantitative data for the evaluation.
"""
from __future__ import annotations
import os
import argparse
import json
from datetime import datetime
import requests
import csv

RAW_DIR = os.path.join(os.path.dirname(__file__), 'raw')
os.makedirs(RAW_DIR, exist_ok=True)


def fetch_sip_status(base_url: str):
    url = base_url.rstrip('/') + '/api/sip/status'
    print(f"Fetching SIP status from {url}")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    timestamp = datetime.utcnow().isoformat()

    out_json = os.path.join(RAW_DIR, 'sip_status.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump({'fetched_at': timestamp, 'data': data}, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_json}")

    # Flatten sipCalls into CSV
    rows = []
    for c in data.get('sipCalls', []):
        rows.append({
            'roomName': c.get('roomName'),
            'callId': c.get('callId'),
            'participants': c.get('participants'),
            'createdAt': c.get('createdAt'),
            'durationSeconds': c.get('durationSeconds'),
        })

    out_csv = os.path.join(RAW_DIR, 'sip_status.csv')
    if rows:
        with open(out_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {out_csv} (n={len(rows)})")
    else:
        print("No sipCalls found in status response")


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--base-url', default=os.getenv('BASE_URL', 'http://localhost:3000'))
    args = p.parse_args()

    try:
        fetch_sip_status(args.base_url)
        print('Done')
    except Exception as e:
        print('Error while fetching status:', e)
        raise

