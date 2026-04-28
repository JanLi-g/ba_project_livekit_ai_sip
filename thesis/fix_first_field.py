#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korrigiere alle first= Felder im Glossar
Ändere: first={Langform (AKRONYM)}
zu:     first={(AKRONYM)}
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: first={...beliebiger inhalt... (AKRONYM)}
# Ersetze mit: first={(AKRONYM)}

# Finde alle Glossar-Einträge mit first Feld
entry_pattern = r'\\newglossaryentry\{gls-([A-Z0-9-]+)\}.*?first=\{([^}]+)\}.*?text=([^,}]+)'
matches = re.finditer(entry_pattern, content, re.DOTALL)

updated_count = 0
for match in matches:
    acronym = match.group(1)
    first_content = match.group(2)
    text_value = match.group(3).strip()

    # Prüfe ob first={Langform (AKRONYM)} Format ist
    if f'({acronym})' in first_content and first_content != f'({acronym})':
        # Ersetze first={...} mit first={(AKRONYM)}
        old_first = f'first={{{first_content}}}'
        new_first = f'first={{({acronym})}}'

        content = content.replace(old_first, new_first)
        updated_count += 1
        print(f'✓ {acronym}: Korrigiert')

with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✓ {updated_count} Einträge korrigiert!')

