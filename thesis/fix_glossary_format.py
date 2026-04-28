#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script zum Hinzufügen von first/text Feldern zu alle Akronyme im Glossar
"""

import re

# Mapping: Akronym -> Langform
ACRONYMS = {
    'PABX': 'Private Automatic Branch Exchange',
    'DPIA': 'Data Protection Impact Assessment',
    'GDPR': 'General Data Protection Regulation',
    'MANO': 'Management and Orchestration',
    'BPO': 'Business Process Outsourcing',
    'EIA': 'Ethical Impact Assessment',
    'ALSA': 'Advanced Linux Sound Architecture',
    'HTTP': 'Hypertext Transfer Protocol',
    'ARI': 'Asterisk REST Interface',
    'VM': 'Virtuelle Maschine',
    'RFC': 'Request for Comments',
    'IETF': 'Internet Engineering Task Force',
    'DID': 'Direct Inward Dialing',
    'NDJSON': 'Newline Delimited JSON',
    'PESQ': 'Perceptual Evaluation of Speech Quality',
    'POLQA': 'Perceptual Objective Listening Quality Assessment',
    'PCM': 'Pulse Code Modulation',
    'TCP': 'Transmission Control Protocol',
    'RTC': 'Real-Time Communication',
    'PJSIP': 'PJSIP-Bibliothek',
    'UDP': 'User Datagram Protocol',
    'JWT': 'JSON Web Token',
    'RMS': 'Root Mean Square',
    'DTMF': 'Dual-Tone Multi-Frequency',
    'DACH': 'Deutschland, Österreich, Schweiz',
    'HTTPS': 'Hypertext Transfer Protocol Secure',
    'NLP': 'Natural Language Processing',
    'ISO': 'International Organization for Standardization',
    'VLAN': 'Virtual Local Area Network',
    'KMS': 'Key Management Service',
    'DSGVO': 'Datenschutz-Grundverordnung',
    'PCM16': 'Pulse Code Modulation 16-Bit',
    'STUN': 'Session Traversal Utilities for NAT',
    'TURN': 'Traversal Using Relays around NAT',
    'KMU': 'Kleine und mittelständische Unternehmen',
    'SIP': 'Session Initiation Protocol',
    'LLM': 'Large Language Model',
    'WebRTC': 'Web Real-Time Communication',
    'VoIP': 'Voice over Internet Protocol',
    'KI': 'Künstliche Intelligenz',
    'AI': 'Artificial Intelligence',
    'API': 'Application Programming Interface',
    'RTP': 'Real-Time Transport Protocol',
    'RTCP': 'RTP Control Protocol',
    'SRTP': 'Secure Real-Time Transport Protocol',
    'DTLS': 'Datagram Transport Layer Security',
    'NAT': 'Network Address Translation',
    'ICE': 'Interactive Connectivity Establishment',
    'ASR': 'Automatic Speech Recognition',
    'STT': 'Speech-to-Text',
    'TTS': 'Text-to-Speech',
    'VAD': 'Voice Activity Detection',
    'MOS': 'Mean Opinion Score',
    'ITU-T': 'International Telecommunication Union',
    'PBX': 'Private Branch Exchange',
    'IVR': 'Interactive Voice Response',
    'NFV': 'Network Function Virtualization',
    'ETSI': 'European Telecommunications Standards Institute',
    'VNF': 'Virtualized Network Function',
    'NFVI': 'Network Function Virtualization Infrastructure',
    'NFVO': 'Network Function Virtualization Orchestration',
    'CDR': 'Call Detail Record',
    'SLA': 'Service Level Agreement',
    'RBAC': 'Role-Based Access Control',
    'TLS': 'Transport Layer Security',
    'mTLS': 'Mutual TLS',
    'DPA': 'Data Processing Agreement',
    'SCC': 'Standard Contractual Clauses',
    'QoS': 'Quality of Service',
    'PII': 'Personally Identifiable Information',
    'CPaaS': 'Communications Platform as a Service',
    'SFU': 'Selective Forwarding Unit',
    'CPU': 'Central Processing Unit',
    'RAM': 'Random Access Memory',
    'JSON': 'JavaScript Object Notation',
    'SDK': 'Software Development Kit',
    'CLI': 'Command-Line Interface',
    'REST': 'Representational State Transfer',
    'UI': 'User Interface',
    'PSTN': 'Public Switched Telephone Network',
    'OSS': 'Open Source Software',
    'SPA': 'Single-Page Application',
    'E2E': 'End-to-End',
    'RAG': 'Retrieval-Augmented Generation',
    'MEC': 'Multi-access Edge Computing',
    'TTL': 'Time-To-Live',
    'YAML': 'YAML Ain\'t Markup Language',
    'LAN': 'Local Area Network',
    'AVV': 'Auftragsverarbeitungsvertrag',
}

# Lese Glossar-Datei
glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Für jeden Akronym: Überprüfe ob first vorhanden
updated_count = 0
for acronym, longform in ACRONYMS.items():
    # Suche nach: \newglossaryentry{gls-ACRONYM}{ ... name=ACRONYM, [kein first] description=
    pattern = rf'(\\newglossaryentry\{{gls-{re.escape(acronym)}\}}\s*\{{\s*type=fachwort,\s*name={re.escape(acronym)},\s*)'

    # Prüfe ob bereits first vorhanden
    if f'gls-{acronym}' in content:
        has_first = f'gls-{acronym}' in content and 'first=' in content[content.find(f'gls-{acronym}'):content.find(f'gls-{acronym}') + 500]

        # Besser: Direkt nach dem Eintrag suchen
        entry_pattern = rf'\\newglossaryentry\{{gls-{re.escape(acronym)}\}}.*?\\glsadd\{{gls-{re.escape(acronym)}\}}'
        match = re.search(entry_pattern, content, re.DOTALL)

        if match:
            entry_text = match.group(0)
            if 'first=' not in entry_text:
                # Füge first und text nach name ein
                new_entry = re.sub(
                    rf'(name={re.escape(acronym)},)',
                    rf'name={acronym},\n  first={{{longform} ({acronym})}},\n  text={acronym},',
                    entry_text,
                    count=1
                )
                content = content.replace(entry_text, new_entry)
                updated_count += 1
                print(f'✓ {acronym}: first/text hinzugefügt')
            else:
                print(f'- {acronym}: hat bereits first/text')

# Schreibe zurück
with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✓ {updated_count} Akronyme aktualisiert!')
print(f'✓ Glossar erfolgreich aktualisiert!')

