from pathlib import Path
p=Path(__file__).resolve().parent/"sources/icalp2026-79/official-source.tex"
s=p.read_text()
p.write_text(s.replace(r"\mathbf{\Pi}",r"\boldsymbol{\Pi}"))
