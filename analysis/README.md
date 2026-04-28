Evaluation analysis helpers

Folder structure:
- analysis/raw/        # raw JSON/CSV collected from the running system
- analysis/processed/  # processed outputs (summary CSVs, reports, plots)
- analysis/*.py        # small helper scripts

Quick start:
1. Run the system (Next.js dev server + LiveKit + Agent Worker) so the API endpoints are reachable.
2. Collect SIP status:

   python analysis/collect_from_api.py --base-url http://localhost:3000

3. Process the collected status:

   python analysis/parse_sip_status.py

4. If you have more detailed events (analysis/raw/events.csv) you can run latency analysis:

   python analysis/latency_analysis_template.py

Requirements:
- requests
- pandas
- matplotlib (optional for plots)

Notes:
- The scripts are intentionally small and conservative: they do not alter the running system.
- If you want, I can add instrumentation code to the Python Agent Worker to emit newline-delimited JSON events to analysis/raw/events.log

