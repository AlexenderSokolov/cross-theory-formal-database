from pathlib import Path
import json,sys,subprocess
lane=Path(__file__).resolve().parent
ids=['2502.17629','2403.03067','2401.15384','2305.08489','2402.15995','2408.15377','2207.11071','2210.02167','2305.11580','2311.10204']
paths=[p for p in sorted(lane.glob('CP01A13326-CL-*/task.json')) if any(a in json.loads(p.read_text())['source_id'] for a in ids)]
if '--representatives' in sys.argv:
 seen=set();selected=[]
 for p in paths:
  source=json.loads(p.read_text())['source_id']
  if source not in seen:selected.append(str(p));seen.add(source)
 paths=selected
elif len(sys.argv)>1:paths=sys.argv[1:]
raise SystemExit(subprocess.call([sys.executable,str(lane/'compile_cached_four.py'),*map(str,paths)]))
