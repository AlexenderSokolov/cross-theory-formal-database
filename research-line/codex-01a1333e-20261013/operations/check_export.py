from pathlib import Path
import json,sqlite3,subprocess,sys,tempfile
P=Path(__file__).resolve().parent.parent
python=sys.executable
F=Path(tempfile.mkdtemp(prefix='export-check-',dir=P/'.work'))/'research-line'/'fixture'
(F/'operations').mkdir(parents=True);(F/'jobs').mkdir()
(F/'operations/export_materials.py').write_text((P/'operations/export_materials.py').read_text())
for lane in ['metric-decompositions','persistence-modules','local-coloring-linear-logic']:(F/lane).symlink_to(P/lane,target_is_directory=True)
for job in (P/'jobs').iterdir():(F/'jobs'/job.name).symlink_to(job,target_is_directory=True)
foreign=F/'jobs/foreign/r001';foreign.mkdir(parents=True);(foreign/'job-state.json').write_text(json.dumps({'status':'compiled_pending_qa','task_id':'CP13-foreign'}))
def run(batch,limit=25):
 result=subprocess.run([python,str(F/'operations/export_materials.py'),'--batch',batch,'--limit',str(limit)],text=True,capture_output=True)
 assert result.returncode==0,result.stderr
 D=F/'delivery'/batch
 ids=set(json.loads((D/'SELECTION.json').read_text())['task_ids'])
 assert ids=={json.loads(l)['task_id'] for l in (D/'ITEMS.jsonl').read_text().splitlines()}
 with sqlite3.connect(D/'corpus.sqlite3') as db:assert ids=={r[0] for r in db.execute("SELECT task_id FROM problems WHERE state='prepared_unpublished'")}
 assert all(k.startswith('CP01A1333E-') for k in ids)
 return ids
first=run('batch-001',2);assert len(first)==2
(F/'delivery/batch-001/UPLOADED.json').write_text(json.dumps({'task_ids':sorted(first)}))
second=run('batch-002');assert second and first.isdisjoint(second)
excluded=sorted(second)[0];(F/'delivery/EXCLUDED.json').write_text(json.dumps({'task_ids':[excluded]}))
third=run('batch-002');assert third==second-{excluded}
with sqlite3.connect(F/'delivery/batch-002/corpus.sqlite3') as db:assert db.execute('SELECT state FROM problems WHERE task_id=?',(excluded,)).fetchone()[0]=='excluded_from_current_selection'
assert run('batch-002')==third
assert set(json.loads((F/'delivery/batch-001/SELECTION.json').read_text())['task_ids'])==first
(F/'operations/run_export.sh').write_text((P/'operations/run_export.sh').read_text())
r=subprocess.run(['bash',str(F/'operations/run_export.sh'),'--batch','batch-003','--limit','1'],text=True,capture_output=True)
assert r.returncode==0,r.stderr
marker=F/'delivery/batch-003/SELECTION.json'
assert marker.exists(),'run_export.sh did not forward --batch'
assert len(json.loads(marker.read_text())['task_ids'])==1,'run_export.sh did not forward --limit'
print('PASS: own-prefix only; second batch preserves first; no uploaded repeat; excluded rows inactive; repeat export stable. Real compiled products reused; fixture stays in .work.')
