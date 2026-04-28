#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korrigiere type-Felder im Glossar:
- Alle UPPERCASE name → type=akronym
- Alle Mixed-case name → type=fachwort
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Suche nach \newglossaryentry
    if '\\newglossaryentry{gls-' in line:
        # Sammle den kompletten Eintrag
        entry_lines = [line]
        i += 1

        # Lese bis zur schließenden }
        brace_count = line.count('{') - line.count('}')
        while brace_count > 0 and i < len(lines):
            entry_lines.append(lines[i])
            brace_count += lines[i].count('{') - lines[i].count('}')
            i += 1

        # Extrahiere name= Feld
        entry_text = ''.join(entry_lines)
        name_match = re.search(r'name=([A-Za-z0-9-]+)', entry_text)

        if name_match:
            name = name_match.group(1)

            # Bestimme korrekten type
            if name.isupper():
                correct_type = 'akronym'
            else:
                correct_type = 'fachwort'

            # Ersetze type= Feld
            entry_text = re.sub(
                r'type=[^,}]+,',
                f'type={correct_type},',
                entry_text
            )

            output_lines.append(entry_text)
        else:
            output_lines.append(entry_text)
    else:
        output_lines.append(line)
        i += 1

# Schreibe zurück
with open(glossary_path, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("✓ Alle type-Felder korrigiert!")
print("  - UPPERCASE names → type=akronym")
print("  - Mixed-case names → type=fachwort")

