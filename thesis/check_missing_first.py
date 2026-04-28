#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identifiziere Akronyme OHNE first/text Felder
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Finde ALLE newglossaryentry Zeilen
all_acronyms = re.findall(r'newglossaryentry\{gls-([A-Z0-9-]+)\}', content)
all_acronyms_unique = sorted(set(all_acronyms))

# Finde Akronyme MIT first
with_first = re.findall(r'gls-([A-Z0-9-]+)\}.*?first=', content, re.DOTALL)
with_first_unique = set(with_first)

# Unterschied
missing_first = [a for a in all_acronyms_unique if a not in with_first_unique]

print(f"Akronyme GESAMT: {len(all_acronyms_unique)}")
print(f"Akronyme MIT first=: {len(with_first_unique)}")
print(f"Akronyme OHNE first=: {len(missing_first)}")
print(f"\nAkronyme OHNE first/text:")
for acr in missing_first[:30]:  # Zeige erste 30
    print(f"  - {acr}")

if len(missing_first) > 30:
    print(f"  ... und {len(missing_first) - 30} weitere")

