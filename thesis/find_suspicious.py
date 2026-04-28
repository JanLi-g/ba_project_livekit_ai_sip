#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finde alle type=fachwort Einträge, die Akronyme sein sollten
(d.h. name mit vielen Großbuchstaben)
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Finde alle Einträge mit type=fachwort
entries = re.finditer(
    r'\\newglossaryentry\{gls-[^}]+\}\{[^}]*type=fachwort,[^}]*name=([A-Za-z0-9-]+)',
    content,
    re.DOTALL
)

suspicious = []
for match in entries:
    name = match.group(1)

    # Zähle Großbuchstaben
    uppercase_count = sum(1 for c in name if c.isupper())
    total_letters = sum(1 for c in name if c.isalpha())

    # Wenn >50% Großbuchstaben oder mehrere Großbuchstaben + Bindestriche, ist es wahrscheinlich ein Akronym
    if total_letters > 0:
        uppercase_ratio = uppercase_count / total_letters
        if uppercase_ratio > 0.5 or (uppercase_count >= 2 and '-' in name):
            suspicious.append(name)
            print(f'Verdacht: {name} (type=fachwort) - sollte akronym sein')

if not suspicious:
    print('✓ Keine verdächtigen Einträge gefunden!')
else:
    print(f'\n⚠️  {len(suspicious)} verdächtige Einträge')

