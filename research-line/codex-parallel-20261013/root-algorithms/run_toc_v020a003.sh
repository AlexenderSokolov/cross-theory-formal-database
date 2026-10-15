#!/usr/bin/env bash
set -euo pipefail
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:"$PATH"
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PY'
from pathlib import Path
import sys,json
R=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013')
P=R/'research-line/codex-parallel-20261013'
sys.path.insert(0,str(R/'corpus-work/scripts'))
import prepared_delivery as d
for tid,rev in [('CP13-CL-tensor-clifford-observable-dimension-independent-rigidity','r003'),('CP13-CL-quasilinear-two-prover-quantum-delegation-protocols','r002')]:
    state=P/'jobs'/tid/rev/'job-state.json'
    if state.exists() and json.loads(state.read_text()).get('status')=='compiled_pending_qa':
        print('Reuse successful product:',state.parent)
    else:
        print(d.assemble(P/'combinatorics-logic'/tid/'task.json',P,P/'jobs',material_only=True))
PY
