#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finale Überprüfung: Sind alle type-Klassifizierungen korrekt?
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Liste der echten Akronyme
REAL_ACRONYMS = {
    'AI', 'ALSA', 'API', 'ARI', 'ASR', 'AVV', 'BPO', 'CDR', 'CLI', 'CPU', 'DACH',
    'DID', 'DPIA', 'DPA', 'DSGVO', 'DTFS', 'DTLS', 'DTMF', 'E2E', 'EIA', 'ETSI', 'GDPR',
    'HTTPS', 'HTTP', 'ICE', 'IETF', 'ISO', 'ITU-T', 'IVR', 'JWT', 'JSON', 'KI', 'KMS',
    'KMU', 'LAN', 'LLM', 'MANO', 'MEC', 'MOS', 'mTLS', 'NAT', 'NDJSON', 'NFV', 'NFVI', 'NFVO',
    'NLP', 'OSS', 'PABX', 'PBX', 'PCM', 'PCM16', 'PESQ', 'PII', 'PJSIP', 'POLQA', 'PSTN',
    'QoS', 'RBAC', 'RFC', 'RAM', 'RAG', 'REST', 'RMS', 'RTC', 'RTP', 'RTCP', 'SDK',
    'SFU', 'SIP', 'SLA', 'SPA', 'SCC', 'SRTP', 'STT', 'STUN', 'TCP', 'TLS', 'TTL',
    'TURN', 'TTS', 'UI', 'UDP', 'VAD', 'VLAN', 'VNF', 'VM', 'VoIP', 'WebRTC', 'YAML'
}

# Finde alle Einträge
entries = re.finditer(
    r'\\newglossaryentry\{gls-([^}]+)\}\{[^}]*type=([a-z]+),[^}]*name=([A-Za-z0-9-]+)',
    content,
    re.DOTALL
)

errors = []
correct = 0
total = 0

for match in entries:
    gls_id = match.group(1)
    actual_type = match.group(2)
    name = match.group(3)

    total += 1

    # Bestimme korrekten Type
    if name in REAL_ACRONYMS:
        correct_type = 'akronym'
    else:
        correct_type = 'fachwort'

    # Überprüfe
    if actual_type != correct_type:
        errors.append({
            'name': name,
            'gls_id': gls_id,
            'actual': actual_type,
            'correct': correct_type
        })
    else:
        correct += 1

print(f"✓ Überprüfung abgeschlossen!")
print(f"✓ Gesamt: {total} Einträge")
print(f"✓ Korrekt: {correct}/{total}")
print(f"✗ Fehler: {len(errors)}")

if errors:
    print(f"\n⚠️  FEHLER GEFUNDEN:")
    for error in errors[:20]:  # Zeige erste 20
        print(f"  {error['name']}: hat type={error['actual']}, sollte type={error['correct']} sein")
    if len(errors) > 20:
        print(f"  ... und {len(errors) - 20} weitere")
else:
    print(f"\n✅ ALLE TYPES SIND KORREKT!")

