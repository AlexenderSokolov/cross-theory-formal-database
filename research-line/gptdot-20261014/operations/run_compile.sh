#!/usr/bin/env bash
set -euo pipefail
O="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
P="$(dirname "$O")"
W="$(dirname "$(dirname "$P")")"
# Optional native BibLaTeX backend; all runtime and PAR cache files stay in this line.
if [[ -x "$P/.work/biber-2.21/bin/biber" ]]; then
  export PATH="$P/.work/biber-2.21/bin:$PATH"
  export TMPDIR="$P/.work/biber-2.21/tmp"
  export PAR_GLOBAL_TMPDIR="$TMPDIR"
  mkdir -p -- "$TMPDIR"
fi
# This cloud image has TeX source files but broken system ls-R/format symlinks.
# Use this lane's cached format and ordinary filesystem lookup, without global changes.
if [[ -f "$P/.work/texmf/web2c/xetex/xelatex.fmt" ]]; then
  export TEXMF="{$P/.work/texmf,/usr/share/texmf,/usr/share/texlive/texmf-dist}"
  export TEXFORMATS="$P/.work/texmf/web2c/xetex:"
fi
exec python3 "$O/compile_material.py" "$@"
