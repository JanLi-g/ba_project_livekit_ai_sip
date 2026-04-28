# ba_project_livekit_ai_sip

Öffentliches Code-Repository für eine LiveKit-/SIP-/Telefonie-Demo.

## Öffentlich
- `app/`
- `python/`
- `powershell/`
- `analysis/`, `evaluation/`, `thesis/` ohne private Rohdaten
- `docker-compose.yml`, `Dockerfile.agent`

## GitHub Quick Setup
```powershell
git clone https://github.com/JanLi-g/ba_project_livekit_ai_sip.git
cd ba_project_livekit_ai_sip
Copy-Item .env.example .env.local
npm install
npm run dev
```

Oder mit Docker:

```powershell
docker compose up --build
```

## Privat lokal
- `.env`, `.env.local`
- echte SIP-/LiveKit-/Telefonie-Zugangsdaten
- Messdaten, Logs und Rohdateien aus `metrics/`, `livekit-data/`, `analysis/raw/`, `analysis/processed/`, `evaluation/logs/`, `evaluation/results/`
- Scratch-/Altbestände wie `thesis/scratches/` und `python/old/`

## Schnellstart
```powershell
Copy-Item .env.example .env.local
npm install
npm run dev
```


## Sicherheit
- Keine echten Secrets, Rufnummern, Tokens oder Project Keys einchecken.
- Vor dem Push nach `key`, `secret`, `token`, `password`, `sip` und echten Nummern suchen.

## Hinweis
Die Konfigurationsdateien sind als Vorlagen gedacht und enthalten nur Platzhalter.

