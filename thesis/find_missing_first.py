#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identifiziere alle Akronyme im Glossar die KEIN first/text haben
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: \newglossaryentry{gls-XXXXX}....\glsadd{gls-XXXXX}
entry_pattern = r'\\newglossaryentry\{gls-([^}]+)\}.*?\\glsadd\{gls-\1\}'
matches = re.finditer(entry_pattern, content, re.DOTALL)

acronyms_without_first = []

for match in matches:
    acronym = match.group(1)
    entry_text = match.group(0)

    # Prüfe: Hat dieser Eintrag first=?
    if 'first=' not in entry_text:
        # Ist es ein Akronym (uppercase) oder Fachwort?
        # Akronyme sind typisch: KI, SIP, VoIP, HTTP, etc.
        if acronym.isupper() or (acronym[0].isupper() and '-' in acronym):
            acronyms_without_first.append(acronym)
            print(f'Akronym OHNE first/text: {acronym}')

print(f'\n\nGesamt: {len(acronyms_without_first)} Akronyme ohne first/text')
print('\nListe:')
for acr in sorted(acronyms_without_first):
    print(f'  - {acr}')

