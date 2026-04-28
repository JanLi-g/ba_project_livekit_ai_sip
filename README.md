# ba_project_livekit_ai_sip

Open-Source-Repo für eine LiveKit-/SIP-/Telefonie-Demo mit Next.js, Python-Helferskripten und Docker-Compose-Setup.

## Projektüberblick
Dieses Projekt verbindet eine Weboberfläche mit einer SIP-/LiveKit-basierten Sprachstrecke. Das Repository ist bewusst in einen öffentlichen Teil und lokale Betriebsdaten getrennt:

- **öffentlich**: Code, Doku und Templates
- **lokal privat**: echte SIP-/LiveKit-Zugangsdaten, Messdaten, Logs und interne Arbeitsordner

## Was öffentlich ist
- `app/` – Next.js Frontend und API-Routen
- `python/` – Setup- und Integrationsskripte
- `docker-compose.yml`, `Dockerfile.agent` – lokale Laufzeit- und Entwicklungsumgebung
- `README.md`, `LICENSE`, `package.json` – Projektinfo und Abhängigkeiten

## Was privat lokal bleiben soll
- `.env`, `.env.local` sowie alle echten Secrets
- echte SIP-/LiveKit-/Telefonie-Zugangsdaten
- Messdaten, Logs und Rohdateien aus `metrics/`, `livekit-data/`
- Scratch-/Altbestände wie `python/old/` und `scratch_sources/`

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

## Voraussetzungen
- Node.js und npm
- optional: Docker / Docker Compose
- lokale Konfigurationsdatei `.env.local` auf Basis von `.env.example`

## Konfiguration
Kopiere zuerst die Beispiel-Datei und trage danach nur lokale Werte ein:

```powershell
Copy-Item .env.example .env.local
```

Typische Werte in `.env.local`:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `SIP_PROVIDER_DOMAIN`
- `SIP_PROVIDER_USERNAME`
- `SIP_PROVIDER_PASSWORD`
- `SIP_DID_NUMBER`

## Schnellstart
```powershell
npm install
npm run dev
```

## Projektstruktur
- `app/` – Weboberfläche und API-Endpunkte
- `python/` – SIP-/LiveKit-Automation und Hilfsskripte
- `public/` – statische Assets
- `docker-compose.yml` – lokale Container-Orchestrierung

## Sicherheit
- Keine echten Secrets, Rufnummern, Tokens oder Project Keys einchecken.
- Vor dem Push nach `key`, `secret`, `token`, `password`, `sip` und echten Nummern suchen.
- Messdaten und Logs nur lokal verwenden.

## Hinweis
Die Konfigurationsdateien im Repo sind als Vorlagen gedacht und enthalten nur Platzhalter.

