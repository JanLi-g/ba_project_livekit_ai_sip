#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reorganisiere glossary.tex:
1. Alle Akronyme (UPPERCASE name) alphabetisch
2. Dann alle Fachwörter (Mixed-case name) alphabetisch
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Finde alle newglossaryentry Blöcke
entry_pattern = r'\\newglossaryentry\{gls-[^}]+\}\{[^}]*\}[\s\n]*\\glsadd\{[^}]+\}'
entries = re.findall(entry_pattern, content, re.DOTALL)

# Sortiere Einträge
acronyms = []  # UPPERCASE names
fachwort = []  # Mixed-case names

for entry in entries:
    # Extrahiere name= Feld
    name_match = re.search(r'name=([A-Za-z0-9-]+)', entry)
    if name_match:
        name = name_match.group(1)

        # Klassifiziere: Ist name vollständig UPPERCASE?
        if name.isupper():
            acronyms.append((name, entry))
        else:
            fachwort.append((name, entry))

# Sortiere alphabetisch
acronyms.sort(key=lambda x: x[0])
fachwort.sort(key=lambda x: x[0])

# Baue neuen Content
new_content = ""
for name, entry in acronyms:
    new_content += entry + '\n'

# Trennlinie/Kommentar zwischen Akronymen und Fachwörtern
new_content += '\n% ==================== FACHWÖRTER ====================\n\n'

for name, entry in fachwort:
    new_content += entry + '\n'

# Schreibe zurück
with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✓ Glossar reorganisiert!")
print(f"  - {len(acronyms)} Akronyme (sortiert)")
print(f"  - {len(fachwort)} Fachwörter (sortiert)")

