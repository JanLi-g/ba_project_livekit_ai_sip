#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finale Korrektur: Setze first={AKRONYM} (ohne runde Klammern) für alle Einträge
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
current_acronym = None

for i, line in enumerate(lines):
    # Suche nach: \newglossaryentry{gls-ACRONYM}
    if '\\newglossaryentry{gls-' in line:
        match = re.search(r'\\newglossaryentry\{gls-([A-Za-z0-9-]+)\}', line)
        if match:
            current_acronym = match.group(1)

    # Suche nach: name=ACRONYM (zur Bestätigung)
    elif 'name=' in line and current_acronym:
        name_match = re.search(r'name=([A-Za-z0-9-]+)', line)
        if name_match:
            name_value = name_match.group(1)
            # name_value sollte gleich current_acronym sein

    # Ersetze first= Zeile
    elif 'first=' in line and current_acronym:
        # Ersetze mit: first={ACRONYM}
        output_lines.append(f'  first={{{current_acronym}}},\n')
        current_acronym = None  # Reset
        continue

    output_lines.append(line)

with open(glossary_path, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("✓ Glossar repariert: Alle first= sind jetzt first={AKRONYM}")

