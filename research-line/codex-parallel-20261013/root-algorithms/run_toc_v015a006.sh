#!/usr/bin/env bash
set -euo pipefail
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PY'
from pathlib import Path
import sys,json
R=Path("/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013");P=R/"research-line/codex-parallel-20261013"
sys.path.insert(0,str(R/"corpus-work/scripts"))
import prepared_delivery as d
tp=P/"combinatorics-logic/CP13-CL-gaussian-noise-stability-computable-dimension-reduction/task.json"
t=json.loads(tp.read_text());rev=t["revision"];receipt=P/"jobs"/t["task_id"]/rev/("receipts-root-"+rev)/(t["task_id"]+".json")
if receipt.exists() and json.loads(receipt.read_text()).get("ok"):
 print("Successful author-proof artifact retained; no recompilation.")
else:
 print(d.assemble(tp,P,P/"jobs",material_only=True))
PY
