#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorganisiere glossary.tex:
1. Alle type=akronym Einträge alphabetisch nach name
2. Dann alle type=fachwort Einträge alphabetisch nach name
3. Alles in EINEM Glossar
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Splitte Content in einzelne Einträge
# Pattern: \newglossaryentry{...} bis \glsadd{...}
entries = []
current_entry = ""
in_entry = False

for line in content.split('\n'):
    if '\\newglossaryentry{gls-' in line:
        if current_entry:
            entries.append(current_entry)
        current_entry = line + '\n'
        in_entry = True
    elif in_entry:
        current_entry += line + '\n'
        if '\\glsadd{gls-' in line:
            in_entry = False

if current_entry:
    entries.append(current_entry)

print(f"Gefundene Einträge: {len(entries)}")

# Klassifiziere und extrahiere name + type
akronyme = []
fachwort = []

for entry in entries:
    # Extrahiere name
    name_match = re.search(r'name=([A-Za-z0-9-]+)', entry)
    # Extrahiere type
    type_match = re.search(r'type=([a-z]+)', entry)

    if name_match and type_match:
        name = name_match.group(1)
        typ = type_match.group(1)

        if typ == 'akronym':
            akronyme.append((name, entry))
        else:
            fachwort.append((name, entry))

# Sortiere beide Listen alphabetisch
akronyme.sort(key=lambda x: x[0].lower())
fachwort.sort(key=lambda x: x[0].lower())

print(f"Akronyme: {len(akronyme)}")
print(f"Fachwörter: {len(fachwort)}")

# Baue neuen Content: Akronyme zuerst, dann Fachwörter
new_content = ""

# Akronyme
for name, entry in akronyme:
    new_content += entry + '\n'

# Fachwörter
for name, entry in fachwort:
    new_content += entry + '\n'

# Schreibe zurück
with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✓ Glossar reorganisiert!")
print(f"  - {len(akronyme)} Akronyme (alphabetisch)")
print(f"  - {len(fachwort)} Fachwörter (alphabetisch)")
print(f"  - Alles in EINEM Glossar")

