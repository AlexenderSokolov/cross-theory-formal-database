"""Preserve the declared existing origin enum in this lane's assembled package."""
import argparse, json
from pathlib import Path
ALLOWED={'human_authored_native_tex','human_authored_proof_assistant_transcription','human_authored_checked_published_transcription'}
def apply(job):
 job=Path(job).resolve()
 state=json.loads((job/'job-state.json').read_text())
 if state['status']!='assembled':raise ValueError('Apply origin before compilation, to an assembled job only')
 pkg=job/state['package']; task=json.loads((pkg/state['task_snapshot']).read_text())
 origin=task.get('origin_class')
 if origin not in ALLOWED:raise ValueError('Task must explicitly declare an existing supported origin_class')
 mf=pkg/'manifest.json'; manifest=json.loads(mf.read_text())
 if len(manifest['items'])!=1:raise ValueError('Expected one material per job')
 row=manifest['items'][0]; pf=pkg/'sources'/row['problem_id']/'provenance.json'
 provenance=json.loads(pf.read_text()); row['origin_class']=origin; provenance['origin_class']=origin
 mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 pf.write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
 return {'origin_class':origin,'job':str(job)}
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--job',required=True,type=Path)
 print(json.dumps(apply(parser.parse_args().job)))
