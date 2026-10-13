#!/usr/bin/env bash
set -euo pipefail
lane="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
task_root="$(dirname -- "$lane")"
repo="$(dirname -- "$(dirname -- "$task_root")")"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
export PYTHONPATH="$repo/corpus-work/scripts${PYTHONPATH:+:$PYTHONPATH}"
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - "$task_root" "$lane/jobs" "$@" <<'PY'
import pathlib,sys
import prepared_delivery
root=pathlib.Path(sys.argv[1]); out=pathlib.Path(sys.argv[2])
if len(sys.argv)<4: raise SystemExit('Pass explicit relative task.json paths; successful jobs must not be rerun.')
for task in sys.argv[3:]:
 print(prepared_delivery.assemble(root/task,root,out,material_only=True))
PY
