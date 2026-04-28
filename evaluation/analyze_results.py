#!/usr/bin/env python3
"""
Evaluation Data Analysis Script
Für die Verarbeitung und Analyse der Evaluationsergebnisse
"""

import json
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from scipy import stats

class EvaluationAnalyzer:
    """Hauptklasse für die Evaluationsdatenanalyse"""

    def __init__(self, results_dir="evaluation/results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.data = {}

    # ==================== LATENZ-ANALYSE ====================

    def analyze_latencies(self, calls_data):
        """
        Analysiert End-to-End Latenzen und Komponenten-Breakdown

        Args:
            calls_data: Liste von Dicts mit Latenz-Komponenten

        Returns:
            dict mit Statistiken
        """
        df = pd.DataFrame(calls_data)

        results = {
            'e2e_latency': {
                'mean': df['e2e_latency'].mean(),
                'median': df['e2e_latency'].median(),
                'std': df['e2e_latency'].std(),
                'min': df['e2e_latency'].min(),
                'max': df['e2e_latency'].max(),
                'p95': df['e2e_latency'].quantile(0.95),
                'count': len(df)
            },
            'components': {
                'network': df['network_latency'].mean(),
                'buffering': df['buffering_latency'].mean(),
                'stt': df['stt_latency'].mean(),
                'llm': df['llm_latency'].mean(),
                'tts': df['tts_latency'].mean(),
            }
        }

        # Komponenten-Anteile berechnen
        total = sum(results['components'].values())
        results['component_percentages'] = {
            k: (v/total)*100 for k, v in results['components'].items()
        }

        return results

    def latency_by_prompt_length(self, calls_data):
        """
        Vergleicht Latenzen nach Prompt-Länge

        Returns:
            dict mit Statistiken pro Kategorie + t-test Ergebnisse
        """
        df = pd.DataFrame(calls_data)

        short = df[df['prompt_category'] == 'short']['e2e_latency']
        medium = df[df['prompt_category'] == 'medium']['e2e_latency']
        long = df[df['prompt_category'] == 'long']['e2e_latency']

        # Statistiken
        results = {
            'short': {
                'mean': short.mean(),
                'std': short.std(),
                'count': len(short)
            },
            'medium': {
                'mean': medium.mean(),
                'std': medium.std(),
                'count': len(medium)
            },
            'long': {
                'mean': long.mean(),
                'std': long.std(),
                'count': len(long)
            }
        }

        # t-test: kurz vs. lang
        t_stat, p_value = stats.ttest_ind(short, long)
        cohens_d = (long.mean() - short.mean()) / np.sqrt(
            ((len(short)-1)*short.std()**2 + (len(long)-1)*long.std()**2) /
            (len(short) + len(long) - 2)
        )

        results['statistical_test'] = {
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'significant_alpha_0_01': p_value < 0.01
        }

        return results

    # ==================== AUDIO-QUALITÄT ====================

    def analyze_mos_scores(self, mos_data):
        """
        Analysiert Mean Opinion Score Bewertungen

        Args:
            mos_data: Liste von MOS-Bewertungen (1-5)

        Returns:
            dict mit Statistiken und Kategorisierung
        """
        df = pd.DataFrame(mos_data)

        # Kategorisierung
        excellent = len(df[df['mos'] == 5])
        good = len(df[df['mos'] == 4])
        acceptable = len(df[df['mos'] == 3])
        bad = len(df[df['mos'] <= 2])
        total = len(df)

        results = {
            'categories': {
                'excellent_5': {
                    'count': excellent,
                    'percentage': (excellent/total)*100
                },
                'good_4': {
                    'count': good,
                    'percentage': (good/total)*100
                },
                'acceptable_3': {
                    'count': acceptable,
                    'percentage': (acceptable/total)*100
                },
                'bad_1_2': {
                    'count': bad,
                    'percentage': (bad/total)*100
                }
            },
            'aggregate': {
                'mean': df['mos'].mean(),
                'median': df['mos'].median(),
                'std': df['mos'].std(),
                'total_calls': total,
                'geq_4_percentage': ((excellent + good)/total)*100
            }
        }

        return results

    def analyze_rtp_metrics(self, rtp_data):
        """
        Analysiert RTP-Netzwerk-Metriken
        """
        df = pd.DataFrame(rtp_data)

        return {
            'jitter': {
                'mean_ms': df['jitter_ms'].mean(),
                'min_ms': df['jitter_ms'].min(),
                'max_ms': df['jitter_ms'].max(),
                'std_ms': df['jitter_ms'].std()
            },
            'packet_loss': {
                'mean_percent': df['packet_loss_percent'].mean(),
                'min_percent': df['packet_loss_percent'].min(),
                'max_percent': df['packet_loss_percent'].max(),
                'std_percent': df['packet_loss_percent'].std()
            },
            'bitrate': {
                'mean_kbps': df['bitrate_kbps'].mean(),
                'min_kbps': df['bitrate_kbps'].min(),
                'max_kbps': df['bitrate_kbps'].max(),
            }
        }

    # ==================== RESSOURCEN-ANALYSE ====================

    def analyze_cpu_scaling(self, load_test_data):
        """
        Analysiert CPU-Skalierung mit parallelen Calls

        Args:
            load_test_data: Liste von Dicts mit {num_calls, cpu_percent}
        """
        df = pd.DataFrame(load_test_data)

        # Gruppieren nach Anzahl Calls
        grouped = df.groupby('num_calls')['cpu_percent'].agg(['mean', 'std', 'min', 'max', 'count'])

        # Lineare Regression
        X = df['num_calls'].values.reshape(-1, 1)
        y = df['cpu_percent'].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(X.flatten(), y)

        results = {
            'by_call_count': grouped.to_dict('index'),
            'linear_model': {
                'formula': f'CPU = {intercept:.1f}% + {slope:.1f}% × num_calls',
                'r_squared': r_value**2,
                'p_value': p_value,
                'std_error': std_err
            }
        }

        return results

    def analyze_ram_scaling(self, load_test_data):
        """Ähnlich zu CPU aber für RAM"""
        df = pd.DataFrame(load_test_data)
        grouped = df.groupby('num_calls')['ram_mb'].agg(['mean', 'std', 'min', 'max'])

        return {
            'by_call_count': grouped.to_dict('index'),
            'per_call_avg': {
                'idle': grouped.loc[0, 'mean'] if 0 in grouped.index else None,
                'call_1': grouped.loc[1, 'mean'] - grouped.loc[0, 'mean'] if 1 in grouped.index else None,
                'call_2': grouped.loc[2, 'mean'] - grouped.loc[1, 'mean'] if 2 in grouped.index else None,
                'call_3': grouped.loc[3, 'mean'] - grouped.loc[2, 'mean'] if 3 in grouped.index else None,
            }
        }

    # ==================== SIP-INTEGRATION ====================

    def analyze_sip_results(self, sip_calls_data):
        """
        Analysiert SIP-Integrationsergebnisse

        Args:
            sip_calls_data: Liste von SIP-Call Dicts mit Status und Metriken
        """
        df = pd.DataFrame(sip_calls_data)
        total = len(df)

        results = {
            'signaling': {
                'invite_received': (df['invite_ok'].sum() / total * 100),
                'room_created': (df['room_ok'].sum() / total * 100),
                'agent_connected': (df['agent_ok'].sum() / total * 100),
            },
            'media': {
                'audio_downlink_success': (df['audio_ok'].sum() / total * 100),
                'success_count': df['audio_ok'].sum(),
                'fail_count': (~df['audio_ok']).sum(),
            },
            'quality_when_successful': {
                'mos_mean': df[df['audio_ok']]['mos'].mean(),
                'mos_range': (df[df['audio_ok']]['mos'].min(),
                            df[df['audio_ok']]['mos'].max()),
            }
        }

        return results

    # ==================== KOSTEN-ANALYSE ====================

    def analyze_api_costs(self, api_usage_data):
        """
        Analysiert OpenAI API Verbrauch und Kosten

        Tier-1 Preise (aktuell):
        - Whisper: $0.02 pro Minute Audio
        - GPT-4o-mini: $0.00015 pro Input-Token, $0.0006 pro Output-Token
        - TTS: $0.015 pro 1000 Zeichen
        """
        df = pd.DataFrame(api_usage_data)

        # Preise definieren
        whisper_price_per_min = 0.02
        gpt_input_price_per_k = 0.15
        gpt_output_price_per_k = 0.60
        tts_price_per_k = 0.015

        # Kosten berechnen
        df['whisper_cost'] = df['stt_duration_min'] * whisper_price_per_min
        df['gpt_input_cost'] = df['llm_input_tokens'] / 1000 * gpt_input_price_per_k
        df['gpt_output_cost'] = df['llm_output_tokens'] / 1000 * gpt_output_price_per_k
        df['tts_cost'] = df['tts_characters'] / 1000 * tts_price_per_k
        df['total_cost'] = df['whisper_cost'] + df['gpt_input_cost'] + df['gpt_output_cost'] + df['tts_cost']

        results = {
            'costs': {
                'whisper_avg': df['whisper_cost'].mean(),
                'gpt_avg': (df['gpt_input_cost'] + df['gpt_output_cost']).mean(),
                'tts_avg': df['tts_cost'].mean(),
                'total_avg_per_call': df['total_cost'].mean(),
                'total_avg_per_5min': (df['total_cost'] * 5).mean(),  # hochrechnen
            },
            'token_usage': {
                'stt_tokens_avg': df['stt_duration_min'].mean() * 60 * 0.8,  # ca. 0.8 Token/sec
                'llm_input_avg': df['llm_input_tokens'].mean(),
                'llm_output_avg': df['llm_output_tokens'].mean(),
                'tts_chars_avg': df['tts_characters'].mean(),
            }
        }

        return results

    def analyze_vad_efficiency(self, with_vad, without_vad):
        """
        Vergleicht STT-Aufrufe mit und ohne VAD
        """
        df_with = pd.DataFrame(with_vad)
        df_without = pd.DataFrame(without_vad)

        reduction = (1 - (df_with['stt_requests'].sum() / df_without['stt_requests'].sum())) * 100

        return {
            'stt_requests_with_vad': df_with['stt_requests'].sum(),
            'stt_requests_without_vad': df_without['stt_requests'].sum(),
            'reduction_percent': reduction,
            'cost_savings_percent': reduction  # STT-Kosten sind proportional zu Anfragen
        }

    # ==================== EXPORT ====================

    def export_results_json(self, filename, data):
        """Exportiert Ergebnisse als JSON"""
        path = self.results_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"✓ Exportiert: {path}")

    def export_results_csv(self, filename, df):
        """Exportiert Ergebnisse als CSV"""
        path = self.results_dir / filename
        df.to_csv(path, index=False)
        print(f"✓ Exportiert: {path}")

    def generate_summary_report(self, all_results):
        """Erzeugt eine Zusammenfassung für den Bericht"""
        report = f"""
# Evaluationsergebnisse - Zusammenfassung
Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Hypothesen-Status

| Hypothese | Status | Begründung |
|-----------|--------|-----------|
| H1 Latenz | {'✓' if all_results.get('h1_confirmed') else '✗'} | {all_results.get('h1_reason', '')} |
| H2 Audio-Qualität | {'✓' if all_results.get('h2_confirmed') else '✗'} | {all_results.get('h2_reason', '')} |
| H3 SIP-Integration | {'✓' if all_results.get('h3_confirmed') else '✗'} | {all_results.get('h3_reason', '')} |
| H4 Skalierung | {'✓' if all_results.get('h4_confirmed') else '✗'} | {all_results.get('h4_reason', '')} |
| H5 Kosten | {'✓' if all_results.get('h5_confirmed') else '✗'} | {all_results.get('h5_reason', '')} |

## Messergebnisse

### Web-UI Baseline
- Anzahl Calls: {all_results.get('webui_call_count', 'N/A')}
- Mittlere Latenz: {all_results.get('webui_latency_mean', 'N/A')} ms
- MOS ≥ 4: {all_results.get('webui_mos_geq4_pct', 'N/A')}%
- CPU pro Call: {all_results.get('webui_cpu_per_call', 'N/A')}%

### SIP-Integration
- Anzahl Calls: {all_results.get('sip_call_count', 'N/A')}
- INVITE-Erfolgsquote: {all_results.get('sip_invite_success', 'N/A')}%
- Audio hörbar: {all_results.get('sip_audio_success', 'N/A')}%
- Durchschnittl. MOS: {all_results.get('sip_mos_mean', 'N/A')}

### Lasttests
- CPU-Modell: {all_results.get('cpu_model', 'N/A')}
- R²: {all_results.get('cpu_r_squared', 'N/A')}
- Rate-Limit Erreicht bei: {all_results.get('rate_limit_at_calls', 'N/A')} Calls

## Conclusio
{all_results.get('conclusion', 'Keine Conclusio vorhanden')}
"""

        path = self.results_dir / 'SUMMARY_REPORT.md'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Bericht generiert: {path}")


# ==================== BEISPIELVERWENDUNG ====================

if __name__ == '__main__':
    analyzer = EvaluationAnalyzer()

    # Beispiel: Latenzanalyse
    print("=" * 50)
    print("Evaluations-Analyzer laden")
    print("=" * 50)
    print(f"\nVerzeichnis: {analyzer.results_dir}")
    print("\nVerfügbare Methoden:")
    print("  - analyze_latencies(calls_data)")
    print("  - latency_by_prompt_length(calls_data)")
    print("  - analyze_mos_scores(mos_data)")
    print("  - analyze_cpu_scaling(load_test_data)")
    print("  - analyze_sip_results(sip_calls_data)")
    print("  - analyze_api_costs(api_usage_data)")
    print("  - analyze_vad_efficiency(with_vad, without_vad)")
    print("\nBeispiel-Verwendung:")
    print("""
    # Daten laden
    calls = [...]  # aus JSON/CSV

    # Analysieren
    results = analyzer.analyze_latencies(calls)

    # Exportieren
    analyzer.export_results_json('latencies.json', results)
    """)

