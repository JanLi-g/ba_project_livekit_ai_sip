#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finale Überprüfung: Alle types korrekt?
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# echte Akronyme
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

# Zähle
akronyme_correct = 0
fachwort_correct = 0
errors = []

for match in re.finditer(r'name=([A-Za-z0-9-]+).*?type=([a-z]+)', content, re.DOTALL):
    name = match.group(1)
    actual_type = match.group(2)

    if name in REAL_ACRONYMS:
        if actual_type == 'akronym':
            akronyme_correct += 1
        else:
            errors.append(f'{name}: sollte akronym sein, hat aber {actual_type}')
    else:
        if actual_type == 'fachwort':
            fachwort_correct += 1
        else:
            errors.append(f'{name}: sollte fachwort sein, hat aber {actual_type}')

print(f"✓ Akronyme (korrekt): {akronyme_correct}")
print(f"✓ Fachwörter (korrekt): {fachwort_correct}")
print(f"✗ Fehler: {len(errors)}")

if errors:
    print("\nFehlhafte Einträge:")
    for error in errors[:10]:
        print(f"  - {error}")
else:
    print("\n✅ ALLE TYPES SIND KORREKT!")

