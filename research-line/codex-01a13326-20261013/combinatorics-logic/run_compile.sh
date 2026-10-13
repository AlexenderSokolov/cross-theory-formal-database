#!/usr/bin/env bash
set -euo pipefail
LANE=$(cd "$(dirname "$0")" && pwd)
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - "$LANE" <<'PY'
import json, pathlib, sys
lane = pathlib.Path(sys.argv[1]); task_root = lane.parent
repo = task_root.parent.parent
sys.path.insert(0, str(repo / 'corpus-work/scripts'))
from prepared_delivery import assemble, compile_job
for path in sorted(lane.glob('CP01A13326-CL-*/task.json')):
    task = json.loads(path.read_text()); job = lane / 'jobs' / task['task_id'] / task['revision']
    state = job / 'job-state.json'
    if state.exists():
        status = json.loads(state.read_text()).get('status')
        if status != 'needs_codex':
            print(task['task_id'], 'preserved existing job', status)
            continue
        assemble(path, task_root, lane/'jobs', material_only=True, refresh=True, compile_now=False)
        print(compile_job(job, resume=True))
    else:
        print(assemble(path, task_root, lane/'jobs', material_only=True))
PY
