#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finale Überprüfung: Sind alle Akronyme korrekt in glossary.tex konfiguriert?
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Finde alle Glossar-Einträge
entry_pattern = r'\\newglossaryentry\{gls-([^}]+)\}.*?\\glsadd\{gls-\1\}'
matches = re.finditer(entry_pattern, content, re.DOTALL)

acronyms_correct = []
acronyms_missing_first = []
fachwort = []

for match in matches:
    acronym = match.group(1)
    entry_text = match.group(0)

    # Klassifiziere: Ist es ein Akronym (uppercase)?
    is_acronym = acronym.isupper() or (acronym[0].isupper() and '-' not in acronym and len(acronym) <= 5)
    has_first = 'first=' in entry_text
    has_text = 'text=' in entry_text

    if is_acronym:
        if has_first and has_text:
            acronyms_correct.append(acronym)
        else:
            acronyms_missing_first.append(acronym)
    else:
        fachwort.append(acronym)

print("=" * 60)
print("FINALE ÜBERPRÜFUNG - AKRONYME IN GLOSSAR")
print("=" * 60)

print(f"\n✓ Akronyme MIT first/text Feldern: {len(acronyms_correct)}")
if len(acronyms_correct) <= 20:
    for acr in sorted(acronyms_correct):
        print(f"    - {acr}")

print(f"\n⚠️  Akronyme OHNE first/text Felder: {len(acronyms_missing_first)}")
if acronyms_missing_first:
    for acr in sorted(acronyms_missing_first):
        print(f"    - {acr}")
else:
    print("    (Keine!)")

print(f"\nℹ  Fachwörter (kein first/text nötig): {len(fachwort)}")

print(f"\n" + "=" * 60)
print(f"GESAMT: {len(acronyms_correct) + len(acronyms_missing_first) + len(fachwort)} Einträge")
print(f"AKRONYME OK: {100 - (len(acronyms_missing_first) / (len(acronyms_correct) + len(acronyms_missing_first)) * 100):.0f}%" if (len(acronyms_correct) + len(acronyms_missing_first)) > 0 else "")
print("=" * 60)

if len(acronyms_missing_first) == 0:
    print("\n✅ ALLES PERFEKT - ALLE AKRONYME SIND KORREKT KONFIGURIERT!")
else:
    print(f"\n⚠️  {len(acronyms_missing_first)} Akronyme müssen noch angepasst werden")

