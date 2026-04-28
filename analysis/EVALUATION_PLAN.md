# 📊 Evaluationsplan - KI-Sprach-Assistent mit SIP/LiveKit

## Übersicht

Dieser Plan definiert die vollständige Evaluationsstrategie für die Bachelorarbeit. Ziel ist die objektive, statistisch fundierte Bewertung des entwickelten Voice-Agent-Systems hinsichtlich Performance, Zuverlässigkeit und Ressourceneffizienz.

---

## 1. Hypothesen und Forschungsfragen

### H1: Performance - End-to-End Latenz < 2000ms
- **Frage:** Ist die Gesamtlatenz (Sprache → Agent → Antwort) akzeptabel für interaktive Gespräche?
- **Kriterium:** Mean E2E-Latenz < 2000ms (ITU-T G.114 Cat. 2: acceptable)
- **Messgröße:** `greeting_sent` Event in `events.csv`
- **Analyse:** Deskriptive Statistiken (Mean, Median, Std, P95)
- **Verifikation:** BESTANDEN, wenn Mean < 2000ms

### H2: Zuverlässigkeit - Erfolgsrate > 90%
- **Frage:** Funktioniert das System stabil und fehlerfrei?
- **Kriterium:** > 90% erfolgreiche Events
- **Messgröße:** `status` Feld in Events (success/error)
- **Analyse:** Erfolgsrate pro Event-Type (STT, LLM, TTS)
- **Verifikation:** BESTANDEN, wenn Overall Success Rate > 90%

### H3: Ressourceneffizienz - CPU < 1%, RAM < 100MB
- **Frage:** Ist das System ressourcenschonend in der Container-Umgebung?
- **Kriterium:** CPU Mean < 1%, RAM Max < 100MB pro Container
- **Messgröße:** Docker Stats (cpu_percent, mem_usage_mb)
- **Analyse:** Aggregierte Statistiken pro Container
- **Verifikation:** BESTANDEN, wenn beide Kriterien erfüllt

### H4: Komponentenvergleich - STT < LLM Latenz (signifikant)
- **Frage:** Ist die LLM-Verarbeitung der Engpass im System?
- **Kriterium:** LLM-Latenz > STT-Latenz, signifikanter Unterschied (p < 0.05)
- **Messgröße:** `latency_ms` für stt_request vs llm_request
- **Analyse:** Unabhängiger t-Test, Cohen's d Effektgröße
- **Verifikation:** BESTANDEN, wenn p < 0.05

### H5: SIP-Integration - Asterisk performant
- **Frage:** Belastet der SIP-Server (Asterisk) das System?
- **Kriterium:** Asterisk CPU < 1%, RAM < 100MB
- **Messgröße:** Docker Stats für `asterisk-1` Container
- **Analyse:** Vergleich Asterisk vs. LiveKit Ressourcen
- **Verifikation:** BESTANDEN, wenn beide Kriterien erfüllt

---

## 2. Testszenarien

### 2.1 Testfall 1: Web-UI Baseline (N=30)

**Setup:** Next.js Frontend → LiveKit → Python Agent Worker

**Testprompts (standardisiert):**
- **Kurz (3-5s, N=10):** "Wie geht es dir?", "Wer bist du?"
- **Mittel (8-12s, N=15):** "Erkläre Containerisierung.", "Wie funktioniert SIP?"
- **Lang (15-20s, N=5):** "Beschreibe Cloud-LLMs für Telefonie."

**Durchführung:**
1. Frontend öffnen (localhost:3000)
2. Sprache-Aufnahme starten
3. Prompt sprechen
4. Metriken loggen (agent_worker_evaluation.py)
5. Latenz messen (event_ts, latency_ms)

**Messung:** Alle 5s Docker Stats sammeln

---

### 2.2 Testfall 2: SIP-Integration (N=10)

**Setup:** SIP-Client → Asterisk → LiveKit → Agent Worker

**Prompts:** Dieselben wie TC1, aber über SIP-Trunk (Plusnet)

**Vergleich:** Web vs. SIP Latenzen

---

### 2.3 Testfall 3: Lasttest (parallele Calls)

**Szenarien:**
- Load 1: 1 Call (Baseline)
- Load 2: 2 parallele Calls
- Load 3: 3 parallele Calls

**Messung:** Wie verändert sich Latenz und Ressourcenverbrauch?

---

## 3. Statistische Analyse-Methoden

| Hypothese | Methode | Test | Schwellwert |
|-----------|---------|------|-------------|
| H1 | Deskriptiv | Mean, P95 | < 2000ms |
| H2 | Deskriptiv | % Success | > 90% |
| H3 | Deskriptiv | Mean, Max | < 1% CPU, < 100MB RAM |
| H4 | t-Test | p-value, Cohen's d | p < 0.05 |
| H5 | Deskriptiv | Container Vergleich | < 1%, < 100MB |

---

## 4. Datensammlung: Schritt-für-Schritt

### Phase 1: Setup (vor Test-Calls)
```bash
# 1. Docker-Container starten
docker-compose up -d

# 2. Agent Worker starten (evaluation mode)
python python/agent_worker_evaluation.py

# 3. Docker Stats Collector starten (PowerShell)
./powershell/measure-resources.ps1 -DurationMinutes 30
```

### Phase 2: Test-Calls durchführen (N=30 Web + N=10 SIP)
```bash
# Für jeden Test-Call:
# 1. Prompt in Frontend/SIP sprechen
# 2. Warten auf Agent-Antwort
# 3. Logs prüfen (event_ts, latency_ms)
# 4. CSV wird automatisch gefüllt (events.csv)
```

### Phase 3: Analyse durchführen
```bash
# Nach allen Test-Calls:
python analysis/run_evaluation.py

# Output:
# - latency_summary.csv
# - resource_summary.csv
# - hypothesis_results.csv
# - latency_boxplot.png
# - resource_timeline.png
# - latency_table.tex (kopierbar für Thesis!)
# - resource_table.tex (kopierbar für Thesis!)
```

---

## 5. Ausgabeverzeichnis: `analysis/processed/`

| Datei | Zweck | Format |
|-------|-------|--------|
| `latency_summary.csv` | Latenz-Statistiken pro Event-Type | CSV → Tabelle 6.1 |
| `resource_summary.csv` | Ressourcen-Statistiken pro Container | CSV → Tabelle 6.2 |
| `hypothesis_results.csv` | Hypothesen-Verifikation | CSV → Diskussion |
| `latency_boxplot.png` | Latenz-Verteilung | PNG → Abbildung 6.1 |
| `resource_timeline.png` | Ressourcen über Zeit | PNG → Abbildung 6.2 |
| `latency_table.tex` | LaTeX-Tabelle (Kopieren!) | TEX → Direkt in Thesis |
| `resource_table.tex` | LaTeX-Tabelle (Kopieren!) | TEX → Direkt in Thesis |

---

## 6. Thesis-Struktur (Kapitel 6: Evaluation)

### 6.1 Versuchsaufbau und Metriken
- Testumgebung (Hardware, Software, Container)
- Messgrößen (Latenz, Ressourcen, Erfolgsraten)
- Messmethodik (Reproduzierbarkeit, NTP-Synchronisation)

### 6.2 Hypothesen und Forschungsfragen
- H1-H5 aus Abschnitt 1 dieses Plans
- Begründung für Kriterien (ITU-T G.114, Best Practices)

### 6.3 Testfälle
- Testfall 1: Web Baseline (N=30)
- Testfall 2: SIP Integration (N=10)
- Testfall 3: Lasttest (1/2/3 Calls)

### 6.4 Statistische Methoden
- Tabelle der Analyse-Verfahren (s.o.)
- Normalitätstests (Shapiro-Wilk)
- t-Tests, Cohen's d, Konfidenzintervalle

### 6.5 Ergebnisse: Latenz-Analyse
- **Tabelle 6.1** (latency_table.tex): STT/LLM/TTS/E2E Statistiken
- **Abbildung 6.1** (latency_boxplot.png): Boxplot-Vergleich
- **Text:** H1 & H4 Verifikation + Interpretationen

### 6.6 Ergebnisse: Ressourcen-Analyse
- **Tabelle 6.2** (resource_table.tex): CPU/RAM pro Container
- **Abbildung 6.2** (resource_timeline.png): Zeitreihe
- **Text:** H3 & H5 Verifikation + Skalierbarkeits-Diskussion

### 6.7 Ergebnisse: Zuverlässigkeit
- Erfolgsraten pro Event-Type
- Error-Analyse (häufige Fehlerquellen)
- H2 Verifikation

### 6.8 Diskussion und Hypothesen-Zusammenfassung
- H1-H5: Bestanden? Teilweise? Nicht bestanden?
- Vergleich zu Baseline (ITU-T G.114 Kategorien)
- Limitationen der Evaluation
- Empfehlungen für Verbesserungen

---

## 7. Zeitplan (nach Festplattenkauf)

| Phase | Dauer | Aktion |
|-------|-------|--------|
| Setup | 15 min | Docker containers starten, Agent Worker initialisieren |
| Test-Calls | 45 min | 40 Testfälle durchführen (30 Web + 10 SIP) |
| Analyse | 10 min | `python analysis/run_evaluation.py` ausführen |
| Dokumentation | 60 min | Tabellen/Grafiken in Thesis integrieren, Ergebnisse schreiben |
| **Gesamt** | **~2h** | Alles inklusive Puffer |

---

## 8. Qualitätssicherung

- ✅ CSV-Headers prüfen (events.csv, docker_stats.csv)
- ✅ Zeitquellen synchronisieren (System-NTP)
- ✅ Docker logs auf Fehler prüfen
- ✅ Stichproben-Check: Sind Latenzen realistisch?
- ✅ Vergleich zu ähnlichen Systemen (OpenAI Voice, Deepgram)

---

## 9. Literatur und Standards

- **ITU-T G.114:** One-way transmission time (Kategorie 2: <150ms acceptable, Cat 3: 150-400ms)
- **Cohen's d:** Effektgröße-Interpretation (small=0.2, medium=0.5, large=0.8)
- **Shapiro-Wilk Test:** Normalitätsprüfung (p>0.05 = normal)

---

## 10. Nächste Schritte

1. **Neue Festplatte kaufen** ✅ (extern oder intern)
2. **Nach Festplattenkauf:**
   - Docker-Container ggf. neu starten
   - Test-Call-Phase durchführen (40 Calls)
   - Analyse-Skript ausführen
   - Ergebnisse dokumentieren
3. **Thesis-Kapitel schreiben** basierend auf generiertem Output

---

**Stand:** 2025-12-12  
**Autor:** Evaluation Planning  
**Status:** Ready for Test-Call Phase

