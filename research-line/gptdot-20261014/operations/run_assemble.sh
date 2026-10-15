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
exec python3 "$W/corpus-work/scripts/prepared_delivery.py" assemble --task-root "$P" --output-root "$P/jobs" --material-only "$@"
