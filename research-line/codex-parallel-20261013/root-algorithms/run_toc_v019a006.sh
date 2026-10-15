#!/usr/bin/env bash
set -euo pipefail
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:"$PATH"
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PY'
from pathlib import Path
import sys,json
R=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013')
P=R/'research-line/codex-parallel-20261013'
tid='CP13-CL-dense-random-graph-four-day-majority-consensus'
state=P/'jobs'/tid/'r002/job-state.json'
if state.exists() and json.loads(state.read_text()).get('status')=='compiled_pending_qa':
    print('Reuse successful r002:',state.parent)
else:
    sys.path.insert(0,str(R/'corpus-work/scripts'))
    import prepared_delivery as d
    print(d.assemble(P/'combinatorics-logic'/tid/'task.json',P,P/'jobs',material_only=True))
PY
