#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Korrigiere ALL first= Felder
first={(AKRONYM)} -> first=AKRONYM (ohne Klammern und geschwungene Klammern)
"""

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Ersetze first={(...)} mit first=...
# Pattern: first={(...)}
import re
content = re.sub(r'first=\{\(([A-Z0-9-]+)\)\}', r'first=\1', content)

with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Alle first= Felder korrigiert: first={(AKRONYM)} -> first=AKRONYM")

