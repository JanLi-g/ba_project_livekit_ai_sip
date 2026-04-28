"""
Evaluation Analysis Script - Statistische Auswertung für Bachelorarbeit

Analysiert:
1. Latenz-Metriken (STT, LLM, TTS, End-to-End)
2. Ressourcenverbrauch (CPU, RAM pro Container)
3. Erfolgsraten

Output:
- Zusammenfassungs-Tabellen (CSV)
- Boxplots (PNG)
- LaTeX-Tabellen (direkt kopierbar)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats

# Pfade
BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(exist_ok=True)


def load_events() -> pd.DataFrame:
    """Lädt die Event-Daten vom Agent Worker"""
    csv_path = RAW_DIR / "events.csv"
    if not csv_path.exists():
        print(f"⚠️  Keine events.csv gefunden in {RAW_DIR}")
        print("   Führe zuerst Test-Calls mit agent_worker_evaluation.py durch!")
        return pd.DataFrame()

    df = pd.read_csv(csv_path, parse_dates=["event_ts"])
    print(f"✅ {len(df)} Events geladen aus {csv_path}")
    return df


def load_docker_stats() -> pd.DataFrame:
    """Lädt die Docker-Stats"""
    csv_path = RAW_DIR / "docker_stats.csv"
    if not csv_path.exists():
        print(f"⚠️  Keine docker_stats.csv gefunden in {RAW_DIR}")
        print("   Führe zuerst measure-resources.ps1 aus!")
        return pd.DataFrame()

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    print(f"✅ {len(df)} Docker-Stats geladen aus {csv_path}")
    return df


def analyze_latency(df: pd.DataFrame) -> dict:
    """Analysiert Latenz-Metriken"""
    if df.empty:
        return {}

    # Filtere nur Latenz-Events
    latency_events = ["stt_request", "llm_request", "tts_request", "room_connected", "greeting_sent"]
    lat_df = df[df["event_type"].isin(latency_events) & df["latency_ms"].notna()]

    if lat_df.empty:
        print("⚠️  Keine Latenz-Daten gefunden")
        return {}

    # Gruppierte Statistik
    summary = lat_df.groupby("event_type")["latency_ms"].agg([
        "count", "mean", "median", "std", "min", "max",
        lambda x: np.percentile(x, 95)  # P95
    ])
    summary.columns = ["N", "Mean", "Median", "Std", "Min", "Max", "P95"]
    summary = summary.round(1)

    # Speichern
    out_path = PROCESSED_DIR / "latency_summary.csv"
    summary.to_csv(out_path)
    print(f"💾 Latenz-Summary gespeichert: {out_path}")

    # LaTeX-Tabelle generieren
    latex_table = generate_latex_latency_table(summary)
    latex_path = PROCESSED_DIR / "latency_table.tex"
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex_table)
    print(f"💾 LaTeX-Tabelle gespeichert: {latex_path}")

    return {"summary": summary, "raw": lat_df}


def generate_latex_latency_table(summary: pd.DataFrame) -> str:
    """Generiert eine LaTeX-Tabelle für die Bachelorarbeit"""
    latex = r"""% Auto-generated latency table
\begin{longtable}{|l|r|r|r|r|r|r|r|}
\hline
\textbf{Komponente} & \textbf{N} & \textbf{Mean (ms)} & \textbf{Median} & \textbf{Std} & \textbf{Min} & \textbf{Max} & \textbf{P95} \\
\hline
\endhead
"""

    name_map = {
        "stt_request": "STT (Whisper)",
        "llm_request": "LLM (GPT-4o-mini)",
        "tts_request": "TTS (OpenAI)",
        "room_connected": "Room-Verbindung",
        "greeting_sent": "Begrüßung (E2E)"
    }

    for idx, row in summary.iterrows():
        name = name_map.get(idx, idx)
        latex += f"{name} & {int(row['N'])} & {row['Mean']:.0f} & {row['Median']:.0f} & {row['Std']:.0f} & {row['Min']:.0f} & {row['Max']:.0f} & {row['P95']:.0f} \\\\\n"

    latex += r"""\hline
\end{longtable}
"""
    return latex


def plot_latency_boxplot(lat_df: pd.DataFrame):
    """Erstellt Boxplot für Latenzen"""
    if lat_df.empty:
        return

    plt.figure(figsize=(10, 6))

    # Sortiere nach Median
    order = lat_df.groupby("event_type")["latency_ms"].median().sort_values().index

    # Boxplot
    data = [lat_df[lat_df["event_type"] == t]["latency_ms"].values for t in order]
    labels = [t.replace("_", "\n") for t in order]

    bp = plt.boxplot(data, labels=labels, vert=True, patch_artist=True)

    # Farben
    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
    for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    plt.ylabel("Latenz (ms)")
    plt.title("Latenz-Verteilung nach Komponente")
    plt.grid(axis='y', alpha=0.3)

    out_path = PROCESSED_DIR / "latency_boxplot.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 Boxplot gespeichert: {out_path}")


def analyze_resources(df: pd.DataFrame) -> dict:
    """Analysiert Docker-Ressourcenverbrauch"""
    if df.empty:
        return {}

    # Gruppiere nach Container
    summary = df.groupby("container_name").agg({
        "cpu_percent": ["mean", "max", "std"],
        "mem_usage_mb": ["mean", "max", "std"]
    }).round(2)

    summary.columns = ["CPU_Mean", "CPU_Max", "CPU_Std", "RAM_Mean_MB", "RAM_Max_MB", "RAM_Std_MB"]

    out_path = PROCESSED_DIR / "resource_summary.csv"
    summary.to_csv(out_path)
    print(f"💾 Ressourcen-Summary gespeichert: {out_path}")

    # LaTeX-Tabelle
    latex_table = generate_latex_resource_table(summary)
    latex_path = PROCESSED_DIR / "resource_table.tex"
    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex_table)
    print(f"💾 LaTeX-Tabelle gespeichert: {latex_path}")

    return {"summary": summary, "raw": df}


def generate_latex_resource_table(summary: pd.DataFrame) -> str:
    """Generiert LaTeX-Tabelle für Ressourcenverbrauch"""
    latex = r"""% Auto-generated resource table
\begin{longtable}{|l|r|r|r|r|r|r|}
\hline
\textbf{Container} & \textbf{CPU Mean (\%)} & \textbf{CPU Max} & \textbf{CPU Std} & \textbf{RAM Mean (MB)} & \textbf{RAM Max} & \textbf{RAM Std} \\
\hline
\endhead
"""

    for idx, row in summary.iterrows():
        name = idx.replace("untitled-", "").replace("-1", "")
        latex += f"{name} & {row['CPU_Mean']:.1f} & {row['CPU_Max']:.1f} & {row['CPU_Std']:.1f} & {row['RAM_Mean_MB']:.0f} & {row['RAM_Max_MB']:.0f} & {row['RAM_Std_MB']:.0f} \\\\\n"

    latex += r"""\hline
\end{longtable}
"""
    return latex


def plot_resource_timeline(df: pd.DataFrame):
    """Erstellt Timeline-Plot für Ressourcen"""
    if df.empty:
        return

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    containers = df["container_name"].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(containers)))

    for container, color in zip(containers, colors):
        cdf = df[df["container_name"] == container]
        label = container.replace("untitled-", "").replace("-1", "")

        axes[0].plot(cdf["timestamp"], cdf["cpu_percent"], label=label, color=color, alpha=0.8)
        axes[1].plot(cdf["timestamp"], cdf["mem_usage_mb"], label=label, color=color, alpha=0.8)

    axes[0].set_ylabel("CPU (%)")
    axes[0].set_title("CPU-Auslastung über Zeit")
    axes[0].legend(loc="upper right")
    axes[0].grid(alpha=0.3)

    axes[1].set_ylabel("RAM (MB)")
    axes[1].set_xlabel("Zeit")
    axes[1].set_title("RAM-Nutzung über Zeit")
    axes[1].legend(loc="upper right")
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    out_path = PROCESSED_DIR / "resource_timeline.png"
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 Timeline-Plot gespeichert: {out_path}")


def calculate_success_rates(df: pd.DataFrame) -> dict:
    """Berechnet Erfolgsraten"""
    if df.empty:
        return {}

    # Zähle Sessions
    sessions = df["session_id"].nunique()

    # Zähle erfolgreiche vs. fehlerhafte Events
    success = df[df["status"] == "success"].shape[0]
    errors = df[df["status"] == "error"].shape[0]

    # Erfolgsrate pro Event-Typ
    rates = df.groupby("event_type").apply(
        lambda x: (x["status"] == "success").sum() / len(x) * 100
    ).round(1)

    results = {
        "total_sessions": sessions,
        "total_events": len(df),
        "success_count": success,
        "error_count": errors,
        "overall_success_rate": round(success / (success + errors) * 100, 1) if (success + errors) > 0 else 0,
        "rates_by_type": rates
    }

    print(f"\n📈 Erfolgsraten:")
    print(f"   Sessions: {sessions}")
    print(f"   Erfolgsrate: {results['overall_success_rate']}%")

    return results


def run_statistical_tests(lat_df: pd.DataFrame):
    """Führt statistische Tests durch"""
    if lat_df.empty:
        return

    print("\n📊 Statistische Tests:")

    # t-Test: STT vs LLM Latenz
    stt = lat_df[lat_df["event_type"] == "stt_request"]["latency_ms"]
    llm = lat_df[lat_df["event_type"] == "llm_request"]["latency_ms"]

    if len(stt) > 1 and len(llm) > 1:
        t_stat, p_value = stats.ttest_ind(stt, llm)
        print(f"   t-Test STT vs LLM: t={t_stat:.2f}, p={p_value:.4f}")
        if p_value < 0.05:
            print(f"   → Signifikanter Unterschied (α=0.05)")
        else:
            print(f"   → Kein signifikanter Unterschied")

    # Normalitätstest (Shapiro-Wilk)
    for event_type in lat_df["event_type"].unique():
        data = lat_df[lat_df["event_type"] == event_type]["latency_ms"]
        if len(data) >= 3:
            stat, p = stats.shapiro(data)
            normal = "✓ Normal" if p > 0.05 else "✗ Nicht normal"
            print(f"   Shapiro-Wilk {event_type}: p={p:.4f} {normal}")


def test_hypotheses(lat_df: pd.DataFrame, docker_df: pd.DataFrame):
    """Testet die Haupthypothesen der Evaluation"""
    print("\n🧪 HYPOTHESEN-VERIFIZIERUNG")
    print("=" * 60)

    results = {}

    if lat_df.empty and docker_df.empty:
        print("⚠️  Keine Daten vorhanden für Hypothesentests. Führe zuerst Test-Calls durch.")
        return results

    # H1: End-to-End Latenz < 2000ms
    print("\n📌 H1: End-to-End Latenz < 2000ms")
    if not lat_df.empty and "event_type" in lat_df.columns:
        e2e_data = lat_df[lat_df["event_type"] == "greeting_sent"]["latency_ms"]
        if len(e2e_data) > 0:
            mean_e2e = e2e_data.mean()
            h1_verified = mean_e2e < 2000
            results["H1_E2E_Latency"] = {
                "hypothesis": "E2E-Latenz < 2000ms",
                "verified": h1_verified,
                "mean": round(mean_e2e, 1),
                "std": round(e2e_data.std(), 1),
                "p95": round(np.percentile(e2e_data, 95), 1),
                "n": len(e2e_data)
            }
            status = "✅ VERIFIZIERT" if h1_verified else "❌ NICHT VERIFIZIERT"
            print(f"   {status}: Mean={mean_e2e:.0f}ms, Std={e2e_data.std():.0f}ms, P95={np.percentile(e2e_data, 95):.0f}ms")

    # H2: Erfolgsrate > 90%
    print("\n📌 H2: Erfolgsrate > 90%")
    if not lat_df.empty and "status" in lat_df.columns:
        success = lat_df[lat_df["status"] == "success"].shape[0]
        total = len(lat_df)
        success_rate = (success / total * 100) if total > 0 else 0
        h2_verified = success_rate > 90
        results["H2_SuccessRate"] = {
            "hypothesis": "Erfolgsrate > 90%",
            "verified": h2_verified,
            "success_rate": round(success_rate, 1),
            "count": success,
            "total": total
        }
        status = "✅ VERIFIZIERT" if h2_verified else "❌ NICHT VERIFIZIERT"
        print(f"   {status}: {success_rate:.1f}% ({success}/{total} Events erfolgreich)")

    # H3: Ressourcen im grünen Bereich (CPU < 1%, RAM < 100MB pro Container)
    print("\n📌 H3: Effiziente Ressourcennutzung")
    if not docker_df.empty:
        cpu_ok = (docker_df["cpu_percent"].mean() < 1.0)
        ram_ok = (docker_df["mem_usage_mb"].max() < 100)
        h3_verified = cpu_ok and ram_ok
        results["H3_Resources"] = {
            "hypothesis": "CPU < 1%, RAM < 100MB",
            "verified": h3_verified,
            "cpu_mean": round(docker_df["cpu_percent"].mean(), 2),
            "ram_max": round(docker_df["mem_usage_mb"].max(), 1),
            "cpu_ok": cpu_ok,
            "ram_ok": ram_ok
        }
        status = "✅ VERIFIZIERT" if h3_verified else "❌ TEILWEISE"
        print(f"   {status}: CPU Mean={docker_df['cpu_percent'].mean():.2f}%, RAM Max={docker_df['mem_usage_mb'].max():.0f}MB")

    # H4: STT < LLM Latenz (signifikanter Unterschied?)
    print("\n📌 H4: STT-Latenz < LLM-Latenz (signifikant)")
    if not lat_df.empty and "event_type" in lat_df.columns:
        stt_data = lat_df[lat_df["event_type"] == "stt_request"]["latency_ms"]
        llm_data = lat_df[lat_df["event_type"] == "llm_request"]["latency_ms"]

        if len(stt_data) > 1 and len(llm_data) > 1:
            stt_mean = stt_data.mean()
            llm_mean = llm_data.mean()
            t_stat, p_value = stats.ttest_ind(stt_data, llm_data)

            # Effektgröße (Cohen's d)
            cohens_d = (llm_mean - stt_mean) / np.sqrt((stt_data.std()**2 + llm_data.std()**2) / 2)

            h4_verified = (llm_mean > stt_mean) and (p_value < 0.05)
            results["H4_ComponentDiff"] = {
                "hypothesis": "STT < LLM (signifikant)",
                "verified": h4_verified,
                "stt_mean": round(stt_mean, 1),
                "llm_mean": round(llm_mean, 1),
                "p_value": round(p_value, 4),
                "cohens_d": round(cohens_d, 2),
                "significant": p_value < 0.05
            }
            status = "✅ SIGNIFIKANT" if h4_verified else "⚠️  NICHT SIGNIFIKANT"
            print(f"   {status}: STT={stt_mean:.0f}ms vs LLM={llm_mean:.0f}ms")
            print(f"   t-Test: t={t_stat:.2f}, p={p_value:.4f}, Cohen's d={cohens_d:.2f}")

    # H5: Asterisk-Latenz annehmbar (wenn SIP-Daten vorhanden)
    print("\n📌 H5: Asterisk-Container performant")
    if not docker_df.empty:
        asterisk_data = docker_df[docker_df["container_name"].str.contains("asterisk", case=False)]
        if len(asterisk_data) > 0:
            ast_cpu = asterisk_data["cpu_percent"].mean()
            ast_ram = asterisk_data["mem_usage_mb"].mean()
            h5_verified = (ast_cpu < 1.0) and (ast_ram < 100)
            results["H5_Asterisk"] = {
                "hypothesis": "Asterisk: CPU < 1%, RAM < 100MB",
                "verified": h5_verified,
                "cpu_mean": round(ast_cpu, 2),
                "ram_mean": round(ast_ram, 1)
            }
            status = "✅ VERIFIZIERT" if h5_verified else "⚠️  GRENZFALL"
            print(f"   {status}: CPU={ast_cpu:.2f}%, RAM={ast_ram:.0f}MB")

    return results


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("📊 EVALUATION ANALYSIS - Bachelorarbeit")
    print("=" * 60)
    print()

    # 1. Latenz-Analyse
    print("1️⃣  Latenz-Analyse")
    print("-" * 40)
    events_df = load_events()
    if not events_df.empty:
        lat_results = analyze_latency(events_df)
        if lat_results.get("raw") is not None:
            plot_latency_boxplot(lat_results["raw"])
            run_statistical_tests(lat_results["raw"])
    print()

    # 2. Ressourcen-Analyse
    print("2️⃣  Ressourcen-Analyse")
    print("-" * 40)
    docker_df = load_docker_stats()
    if not docker_df.empty:
        analyze_resources(docker_df)
        plot_resource_timeline(docker_df)
    print()

    # 3. Erfolgsraten
    print("3️⃣  Erfolgsraten")
    print("-" * 40)
    if not events_df.empty:
        calculate_success_rates(events_df)
    print()

    # 4. Hypothesen-Tests
    if not events_df.empty or not docker_df.empty:
        hypothesis_results = test_hypotheses(events_df, docker_df)

        # Speichere Hypothesen-Ergebnisse
        hyp_df = pd.DataFrame(hypothesis_results).T
        hyp_path = PROCESSED_DIR / "hypothesis_results.csv"
        hyp_df.to_csv(hyp_path)
        print(f"\n💾 Hypothesen-Ergebnisse gespeichert: {hyp_path}")

    print("\n" + "=" * 60)
    print("✅ Analyse abgeschlossen!")
    print(f"   Output-Verzeichnis: {PROCESSED_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

