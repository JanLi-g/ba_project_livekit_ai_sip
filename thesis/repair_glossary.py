#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repariere das Glossar: Setze first={AKRONYM} basierend auf dem name= Feld
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Finde alle newglossaryentry Blöcke
entry_pattern = r'(\\newglossaryentry\{gls-([A-Za-z0-9-]+)\}\{[\s\n]*type=fachwort,[\s\n]*name=([A-Za-z0-9-]+),[\s\n]*)first=[^,}]*,'
matches = list(re.finditer(entry_pattern, content, re.DOTALL))

print(f"Gefundene Einträge: {len(matches)}")

# Gehe rückwärts durch die Matches um keine Indizes zu zerstören
for match in reversed(matches):
    full_match = match.group(0)
    preamble = match.group(1)
    gls_id = match.group(2)
    name_value = match.group(3)

    # Ersetze first=[alles] mit first={AKRONYM}
    # Der name_value ist das korrekte Akronym
    new_entry = f'{preamble}first={{{name_value}}},'

    content = content[:match.start()] + new_entry + content[match.end():]
    print(f'✓ {gls_id} (name={name_value}): first={{{name_value}}} gesetzt')

with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✓ Glossar repariert!')

