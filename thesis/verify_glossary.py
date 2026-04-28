#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Statistik: Wie viele echte Akronyme haben first/text?
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: \newglossaryentry{gls-XXXXX}....\glsadd{gls-XXXXX}
entry_pattern = r'\\newglossaryentry\{gls-([^}]+)\}.*?\\glsadd\{gls-\1\}'
matches = re.finditer(entry_pattern, content, re.DOTALL)

acronyms_with_first = []
acronyms_without_first = []
fachwort = []

for match in matches:
    acronym = match.group(1)
    entry_text = match.group(0)

    # Klassifiziere: Ist es ein Akronym (uppercase) oder Fachwort?
    is_acronym = acronym.isupper()
    has_first = 'first=' in entry_text

    if is_acronym:
        if has_first:
            acronyms_with_first.append(acronym)
        else:
            acronyms_without_first.append(acronym)
    else:
        fachwort.append(acronym)

print(f'✓ Echte Akronyme (UPPERCASE) MIT first/text: {len(acronyms_with_first)}')
print(f'✗ Echte Akronyme (UPPERCASE) OHNE first/text: {len(acronyms_without_first)}')
print(f'ℹ Fachwörter (kein first/text nötig): {len(fachwort)}')
print(f'\nGESAMT: {len(acronyms_with_first) + len(fachwort)} Glossar-Einträge')

if acronyms_without_first:
    print(f'\nFehlende Akronyme:')
    for acr in acronyms_without_first:
        print(f'  - {acr}')

