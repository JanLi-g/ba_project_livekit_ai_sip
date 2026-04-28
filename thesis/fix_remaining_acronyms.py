#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korrigiere alle Akronyme im Glossar
- Alle UPPERCASE oder Mixed-UPPERCASE-Akronyme → type=akronym
- Nur echte Fachwörter (mit Leerzeichen oder nur Kleinbuchstaben) → type=fachwort
"""

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Liste bekannter Akronyme (auch Mixed-Case)
KNOWN_ACRONYMS = {
    'mTLS', 'ITU-T', 'RTP-Bridge', 'AI', 'ALSA', 'HTTP', 'ARI', 'VM', 'RFC', 'IETF', 'DID',
    'NDJSON', 'PESQ', 'POLQA', 'PCM', 'TCP', 'RTC', 'PJSIP', 'UDP', 'JWT', 'RMS', 'DTMF',
    'DACH', 'HTTPS', 'NLP', 'ISO', 'VLAN', 'KMS', 'DSGVO', 'PCM16', 'STUN', 'TURN',
    'KMU', 'SIP', 'LLM', 'WebRTC', 'VoIP', 'KI', 'API', 'RTP', 'RTCP', 'SRTP', 'DTLS',
    'NAT', 'ICE', 'ASR', 'STT', 'TTS', 'VAD', 'MOS', 'PBX', 'IVR', 'NFV', 'ETSI', 'VNF',
    'NFVI', 'NFVO', 'CDR', 'SLA', 'RBAC', 'TLS', 'DPA', 'SCC', 'QoS', 'PII', 'CPaaS', 'SFU',
    'CPU', 'RAM', 'JSON', 'SDK', 'CLI', 'REST', 'UI', 'PSTN', 'OSS', 'SPA', 'E2E', 'RAG',
    'MEC', 'TTL', 'YAML', 'LAN', 'AVV', 'PABX', 'DPIA', 'GDPR', 'MANO', 'BPO', 'EIA'
}

output_lines = []
i = 0
changes = 0

while i < len(lines):
    line = lines[i]

    # Suche nach \newglossaryentry
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
        import re
        name_match = re.search(r'name=([A-Za-z0-9-]+)', entry_text)
        if name_match:
            name = name_match.group(1)

            # Bestimme korrekten Type
            if name in KNOWN_ACRONYMS:
                correct_type = 'akronym'
            else:
                correct_type = 'fachwort'

            # Ersetze type= Feld
            entry_text = re.sub(
                r'type=[a-z]+,',
                f'type={correct_type},',
                entry_text
            )

            # Track changes
            old_type_match = re.search(r'type=([a-z]+)', ''.join(entry_lines))
            new_type_match = re.search(r'type=([a-z]+)', entry_text)
            if old_type_match and new_type_match and old_type_match.group(1) != new_type_match.group(1):
                changes += 1
                print(f'✓ {name}: {old_type_match.group(1)} → {new_type_match.group(1)}')

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

