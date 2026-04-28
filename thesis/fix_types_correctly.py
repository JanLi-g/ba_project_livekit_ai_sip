#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korrigiere type-Klassifizierung:
- NUR echte Abkürzungen (vollständig oder überwiegend UPPERCASE) → type=akronym
- Zusammengesetzte Wörter mit Bindestrichen, Leerzeichen, Mixed-Case Wörter → type=fachwort
"""

# Liste der ECHTEN Akronyme (nur reine Abkürzungen)
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

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re
output_lines = []
i = 0
changes = 0

while i < len(lines):
    line = lines[i]

    if '\\newglossaryentry{gls-' in line:
        entry_lines = [line]
        i += 1

        # Sammle kompletten Eintrag
        brace_count = line.count('{') - line.count('}')
        while brace_count > 0 and i < len(lines):
            entry_lines.append(lines[i])
            brace_count += lines[i].count('{') - lines[i].count('}')
            i += 1

        entry_text = ''.join(entry_lines)

        # Extrahiere name
        name_match = re.search(r'name=([A-Za-z0-9-]+)', entry_text)
        if name_match:
            name = name_match.group(1)

            # Bestimme korrekten Type
            if name in REAL_ACRONYMS:
                correct_type = 'akronym'
            else:
                correct_type = 'fachwort'

            # Extrahiere alten Type
            old_type_match = re.search(r'type=([a-z]+)', entry_text)
            old_type = old_type_match.group(1) if old_type_match else 'unknown'

            # Ersetze type= Feld
            entry_text = re.sub(
                r'type=[a-z]+,',
                f'type={correct_type},',
                entry_text
            )

            if old_type != correct_type:
                changes += 1
                print(f'✓ {name}: {old_type} → {correct_type}')

            output_lines.append(entry_text)
        else:
            output_lines.append(entry_text)
    else:
        output_lines.append(line)
        i += 1

# Schreibe zurück
with open(glossary_path, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f'\n✓ {changes} Einträge korrigiert!')

