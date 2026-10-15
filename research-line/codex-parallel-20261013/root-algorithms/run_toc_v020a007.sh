#!/usr/bin/env bash
set -euo pipefail
cd "/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PY'
from pathlib import Path
import sys
R=Path("/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013");P=R/"research-line/codex-parallel-20261013"
sys.path.insert(0,str(R/"corpus-work/scripts"))
import prepared_delivery as d
job=P/"jobs/CP13-CL-tree-inversion-comparison-query-near-sorting-lower-bounds/r002"
if (job/"receipts-root-r002/CP13-CL-tree-inversion-comparison-query-near-sorting-lower-bounds.json").exists():
 print("Existing revision retained; inspect successful receipt instead of rebuilding.")
else:
 print(d.assemble(P/"combinatorics-logic/CP13-CL-tree-inversion-comparison-query-near-sorting-lower-bounds/task.json",P,P/"jobs",material_only=True))
PY
