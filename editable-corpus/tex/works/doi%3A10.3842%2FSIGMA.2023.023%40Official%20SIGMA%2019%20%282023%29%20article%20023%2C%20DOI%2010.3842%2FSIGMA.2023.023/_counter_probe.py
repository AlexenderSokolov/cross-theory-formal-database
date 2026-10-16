# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
lines = open("pinned-original-source.tex", encoding="utf-8").read().split("\n")
envpat = re.compile(r'\\begin\{(Theorem|Corollary|Lemma|Proposition|Definition|Note|Example|Remark)\}')
sec = 0
for i, ln in enumerate(lines, 1):
    if ln.lstrip().startswith("\\section") and re.match(r"\s*\\section\s*[\[{]", ln):
        sec += 1
        if i >= 1720: print("SECTION", sec, "at line", i, ln.strip()[:60])
    m = envpat.search(ln)
    if m and i > 1725 and i < 1830:
        print("  env", m.group(1), "line", i, ln.strip()[:70])
