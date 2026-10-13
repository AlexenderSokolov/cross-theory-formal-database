#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname -- "$here")"
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - "$@" <<'PY'
from pathlib import Path
import subprocess,json,sys
P=Path.cwd();retry=set(sys.argv[1:])
for lane in ['hyperlogic-complexity','modal-fixed-points','optical-diagrammatic-algebra']:
 for tf in sorted((P/lane).glob('CP01A13349-*/task.json')):
  t=json.loads(tf.read_text());sf=P/'jobs'/t['task_id']/t['revision']/'job-state.json'
  if t.get('status')!='ready_for_assembly':continue
  if sf.exists():
   st=json.loads(sf.read_text()).get('status')
   if st=='compiled_pending_qa':continue
   if t['task_id'] not in retry:continue
   cmds=[['bash','operations/run_assemble.sh','--task',str(tf.relative_to(P)),'--refresh','--assemble-only'],['bash','operations/run_compile.sh','--job',str(sf.parent),'--resume']]
  else:cmds=[['bash','operations/run_assemble.sh','--task',str(tf.relative_to(P))]]
  for cmd in cmds:
   r=subprocess.run(cmd,cwd=P,text=True,capture_output=True)
   try:x=json.loads(r.stdout)
   except Exception:x={'output':r.stdout[-1200:],'error':r.stderr[-2000:]}
   print(json.dumps({'task':t['task_id'],'exit':r.returncode,'status':x.get('status'),'pages':x.get('pages'),'detail':x if r.returncode else None}),flush=True)
   if r.returncode:break
PY
