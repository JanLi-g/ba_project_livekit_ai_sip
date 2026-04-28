#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KORRIGIERUNG: Reorganisiere glossary.tex richtig
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Entferne alte Fachwörter-Sektion Falls vorhanden
content = content.replace('% ==================== FACHWÖRTER ====================\n\n', '')

# Finde alle Einträge mit besserer Regex
# Pattern: \newglossaryentry{...} bis \glsadd{...}
entry_pattern = r'(\\newglossaryentry\{gls-[^}]+\}\{(?:[^{}]|(?:\{[^{}]*\}))*\}\s*\\glsadd\{[^}]+\})'
matches = re.finditer(entry_pattern, content, re.DOTALL)

entries_with_names = []
for match in matches:
    entry_text = match.group(1)
    # Extrahiere name= Feld
    name_match = re.search(r'name=([A-Za-z0-9-]+)', entry_text)
    if name_match:
        name = name_match.group(1)
        entries_with_names.append((name, entry_text))

print(f"Gefundene Einträge: {len(entries_with_names)}")

# Klassifiziere und sortiere
acronyms = []
fachwort_list = []

for name, entry in entries_with_names:
    # Akronym wenn name vollständig UPPERCASE (und nicht nur ein Wort mit Bindestrich)
    if name.isupper():
        acronyms.append((name, entry))
    else:
        fachwort_list.append((name, entry))

# Sortiere beide Listen alphabetisch
acronyms.sort(key=lambda x: x[0])
fachwort_list.sort(key=lambda x: x[0])

print(f"Akronyme: {len(acronyms)}")
print(f"Fachwörter: {len(fachwort_list)}")

# Baue neuen Content
new_content = ""
for name, entry in acronyms:
    new_content += entry + '\n'

# Trennlinie
new_content += '\n% ==================== FACHWÖRTER ====================\n\n'

for name, entry in fachwort_list:
    new_content += entry + '\n'

# Schreibe zurück
with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✓ Glossar reorganisiert!")
print(f"  - {len(acronyms)} Akronyme (ALPHABETISCH)")
print(f"  - {len(fachwort_list)} Fachwörter (ALPHABETISCH)")

