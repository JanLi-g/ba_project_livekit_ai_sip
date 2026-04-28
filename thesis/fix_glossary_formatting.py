#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formatiere glossary.tex konsistent:
- Jeder Eintrag gefolgt von genau einer Leerzeile
"""

import re

glossary_path = 'E:/WebstormProjects/untitled/thesis/glossary.tex'
with open(glossary_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Finde alle Einträge: \newglossaryentry{...} bis \glsadd{...}
# Und entferne alle überschüssigen Leerzeilen dazwischen
pattern = r'(\\newglossaryentry\{[^}]+\}\{(?:[^{}]|(?:\{[^{}]*\}))*?\})\n+(\\\glsadd\{[^}]+\})'
replacement = r'\1\n\2'

# Erste Runde: Entferne überschüssige Leerzeilen innerhalb Einträge
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Jetzt sorge für genau eine Leerzeile zwischen Einträgen
# Pattern: \glsadd{...} gefolgt von \newglossaryentry{...}
pattern2 = r'(\\\glsadd\{[^}]+\})\n+(\\\newglossaryentry\{)'
replacement2 = r'\1\n\n\2'

content = re.sub(pattern2, replacement2, content)

# Entferne überschüssige Leerzeilen am Ende
content = content.rstrip() + '\n'

with open(glossary_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Glossar-Formatierung konsistent gemacht!")
print("✓ Jeder Eintrag hat genau eine Leerzeile Abstand")

