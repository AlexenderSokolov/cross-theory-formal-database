from pathlib import Path
import json,sys,subprocess
lane=Path(__file__).resolve().parent
ids=['2305.18647','2306.02189','2210.02773','2402.13385','2305.00425','2307.12120','2211.11860','2401.15683','2409.01221']
paths=sys.argv[1:] if len(sys.argv)>1 else [str(p) for p in lane.glob('CP01A13326-CL-*/task.json') if any(a in json.loads(p.read_text())['source_id'] for a in ids)]
raise SystemExit(subprocess.call([sys.executable,str(lane/'compile_cached_four.py'),*paths]))
