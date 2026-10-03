#!/usr/bin/env python3
"""Build a metadata-only candidate work queue. Never contains complete proof text."""
import argparse, csv, datetime, gzip, hashlib, json, os, sqlite3, tempfile
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--input-dir',type=Path,default=Path(__file__).resolve().parent,help='Directory containing the frozen catalog snapshot')
parser.add_argument('--output',type=Path,default=None,help='New SQLite destination; a different existing file is never overwritten')
args=parser.parse_args()
HERE=args.input_dir.resolve()
DEST=(args.output or HERE/'work_queue.sqlite').resolve()
DEST.parent.mkdir(parents=True,exist_ok=True)
DB=None
def jsonl(name):
 p=HERE/name
 text=gzip.decompress(p.read_bytes()).decode() if p.suffix=='.gz' else p.read_text()
 return [json.loads(line) for line in text.splitlines() if line]
def js(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'))
def entry_key(r):return 'id:'+r['problem_id'] if r['problem_id'] else 'unassigned:'+r['unassigned_candidate_key']
rows=jsonl('candidate_catalog.jsonl');history=jsonl('candidate_record_history.jsonl.gz');works=jsonl('source_works.jsonl');materials=jsonl('materials_inventory.jsonl');counts=json.loads((HERE/'counts_and_reconciliation.json').read_text())
SCHEMA='''PRAGMA foreign_keys=ON;
CREATE TABLE catalog_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE source_groups(work_key TEXT PRIMARY KEY,identity_basis TEXT NOT NULL,titles_json TEXT NOT NULL,authors_json TEXT NOT NULL,urls_json TEXT NOT NULL,versions_json TEXT NOT NULL,licenses_json TEXT NOT NULL);
CREATE TABLE entries(entry_key TEXT PRIMARY KEY,problem_id TEXT UNIQUE,candidate_key TEXT UNIQUE,title TEXT,author TEXT,work_key TEXT REFERENCES source_groups(work_key),source_url TEXT,doi TEXT,source_version TEXT,theorem_locator_json TEXT,difficulty_level TEXT,difficulty_reason TEXT,difficulty_verification TEXT NOT NULL,license TEXT,license_url TEXT,status TEXT NOT NULL,source_approved INTEGER NOT NULL CHECK(source_approved IN(0,1)),github_verified_at_catalog_snapshot INTEGER NOT NULL CHECK(github_verified_at_catalog_snapshot IN(0,1)),safe_local975_member INTEGER NOT NULL CHECK(safe_local975_member IN(0,1)),local1002_member INTEGER NOT NULL CHECK(local1002_member IN(0,1)),historical_status TEXT,hold_reason TEXT,next_action TEXT,selected_metadata_path TEXT,selected_metadata_sha256 TEXT,dedup_aliases_json TEXT NOT NULL);
CREATE TABLE record_refs(ref_id INTEGER PRIMARY KEY,entry_key TEXT NOT NULL REFERENCES entries(entry_key),record_path TEXT NOT NULL,record_sha256 TEXT NOT NULL,record_kind TEXT NOT NULL,id_assignment_basis TEXT NOT NULL,original_identifiers_json TEXT NOT NULL);
CREATE TABLE materials(path TEXT PRIMARY KEY,sha256 TEXT,bytes INTEGER,exists_locally INTEGER NOT NULL CHECK(exists_locally IN(0,1)),export_classification TEXT NOT NULL,roles_json TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE entry_materials(entry_key TEXT NOT NULL REFERENCES entries(entry_key),material_path TEXT NOT NULL REFERENCES materials(path),PRIMARY KEY(entry_key,material_path)) WITHOUT ROWID;
CREATE INDEX entries_status_idx ON entries(status);
CREATE INDEX entries_work_idx ON entries(work_key);
CREATE INDEX entries_doi_idx ON entries(doi);
CREATE INDEX record_refs_entry_idx ON record_refs(entry_key);
'''
# Fail closed on inconsistent snapshot counts before creating or touching a database.
expected_stable=counts['comprehensive_retained_stable_ids']
expected_unassigned=counts['unassigned_candidate_identity_keys']
expected_source_approved=counts['source_approved_ids']
expected_git_verified=counts['github_verified_manifest_ids']
if len(rows)!=counts['total_candidate_catalog_rows']:
 raise ValueError('Snapshot row count does not match candidate_catalog.jsonl')
if sum(bool(r['problem_id']) for r in rows)!=expected_stable or sum(not r['problem_id'] for r in rows)!=expected_unassigned:
 raise ValueError('Snapshot stable/unassigned counts do not match candidate rows')
if sum(bool(r['source_approved1015']) for r in rows)!=expected_source_approved or sum(bool(r['github_verified911']) for r in rows)!=expected_git_verified:
 raise ValueError('Snapshot source/Git counts do not match candidate flags')
if len(works)!=counts['work_identity_groups'] or len(materials)!=counts['materials_inventory_paths']:
 raise ValueError('Snapshot source/material group counts do not match catalog files')
# Fresh same-directory temporary output, atomically promoted only after all checks.
fd,tmpname=tempfile.mkstemp(prefix=DEST.name+'.building-',suffix='.sqlite',dir=DEST.parent)
os.close(fd);DB=Path(tmpname)
con=sqlite3.connect(DB);con.executescript(SCHEMA)
con.executemany('INSERT INTO catalog_meta VALUES(?,?)',[("purpose","METADATA WORK QUEUE; candidate/source management only. This is not the qualified full-proof database in editable-corpus."),("proof_text_included","false"),("snapshot_started_utc",counts['snapshot_started_utc']),("source_approved_snapshot_updated_at",counts['source_approved_snapshot_updated_at']),("snapshot_counts_json",js(counts)),("derivation","candidate_catalog.jsonl + source_works.jsonl + candidate_record_history.jsonl.gz + materials_inventory.jsonl")])
con.executemany('INSERT INTO source_groups VALUES(?,?,?,?,?,?,?)',[(w['work_identity_key'],js(w['identity_basis']),js(w['titles']),js(w['authors']),js(w['source_urls']),js(w['source_versions']),js(w['exact_license_labels'])) for w in works])
entry_values=[]
for r in rows:
 d=r['metadata'];entry_values.append((entry_key(r),r['problem_id'] or None,r['unassigned_candidate_key'] or None,d.get('title',''),str(d.get('author',d.get('authors',''))),r['work_identity_key'] or None,d.get('source_url',''),r['doi_extracted'],d.get('source_version',''),js(d.get('source_locator',d.get('primary_locator',d.get('printed_theorem_number',d.get('tag',''))))),d.get('difficulty_level',d.get('level','')),d.get('difficulty_reason',d.get('reason','')),r['difficulty_verification'],d.get('license',''),d.get('license_url',''),r['status'],int(r['source_approved1015']),int(r['github_verified911']),int(r['safe_local975_member']),int(r['local1002_member']),r['historical_item_status'].get('status',''),r['current_hold'],r['next_action'],r['selected_metadata_path'],r['selected_metadata_sha256'],js(r['dedup_identity_aliases'])))
con.executemany('INSERT INTO entries VALUES('+','.join('?'*26)+')',entry_values)
refrows=[]
for h in history:
 for ref in h['record_refs']:refrows.append((entry_key(h),ref['path'],ref['sha256'],ref['kind'],ref['id_assignment_basis'],js(ref.get('original_identifier_values',{}))))
con.executemany('INSERT INTO record_refs(entry_key,record_path,record_sha256,record_kind,id_assignment_basis,original_identifiers_json) VALUES(?,?,?,?,?,?)',refrows)
con.executemany('INSERT INTO materials VALUES(?,?,?,?,?,?)',[(m['path'],m['actual_sha256'],m['bytes'],int(m['exists_locally']),m['export_classification'],js(m['role'])) for m in materials])
material_pairs={(entry_key(r),ref['path']) for r in rows for ref in r['artifact_refs']}
con.executemany('INSERT INTO entry_materials VALUES(?,?)',sorted(material_pairs))
con.commit()
integrity=[row[0] for row in con.execute('PRAGMA integrity_check')];fk=list(con.execute('PRAGMA foreign_key_check'))
expected={'entries':len(rows),'source_groups':len(works),'record_refs':len(refrows),'materials':len(materials),'entry_materials':len(material_pairs)}
actual={table:con.execute(f'SELECT count(*) FROM {table}').fetchone()[0] for table in expected}
stable=con.execute('SELECT count(*) FROM entries WHERE problem_id IS NOT NULL').fetchone()[0];unassigned=con.execute('SELECT count(*) FROM entries WHERE problem_id IS NULL').fetchone()[0]
status=dict(con.execute('SELECT status,count(*) FROM entries GROUP BY status'))
assert integrity==['ok'] and not fk and actual==expected
assert stable==counts['comprehensive_retained_stable_ids'] and unassigned==counts['unassigned_candidate_identity_keys']
assert status==counts['current_status_distribution']
assert con.execute('SELECT sum(source_approved) FROM entries').fetchone()[0]==expected_source_approved
assert con.execute('SELECT sum(github_verified_at_catalog_snapshot) FROM entries').fetchone()[0]==expected_git_verified
con.close()
size=DB.stat().st_size
assert size<=15*1024*1024,f'Metadata SQLite exceeds15MiB:{size}'
verification={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':'METADATA WORK QUEUE','complete_human_proof_text_included':False,'qualified_proof_database':False,'database_bytes':size,'database_sha256':hashlib.sha256(DB.read_bytes()).hexdigest(),'PRAGMA_integrity_check':integrity,'PRAGMA_foreign_key_check':fk,'row_counts_expected':expected,'row_counts_actual':actual,'stable_id_entries':stable,'unassigned_candidate_keys':unassigned,'status_counts':status,'source_approved_entries':expected_source_approved,'github_verified_at_catalog_snapshot_entries':expected_git_verified,'inputs':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['candidate_catalog.jsonl','source_works.jsonl','candidate_record_history.jsonl.gz','materials_inventory.jsonl']}}
# An existing exact output is accepted idempotently. Any different file remains untouched.
try:
 if DEST.exists():
  if hashlib.sha256(DEST.read_bytes()).hexdigest()!=verification['database_sha256']:
   raise FileExistsError(f'Existing destination differs from this snapshot; refused overwrite: {DEST}')
  disposition='existing_exact_database_reused'
 else:
  # Hard-link publication refuses a racing existing file and is atomic on the same filesystem.
  os.link(DB,DEST)
  disposition='fresh_database_created_atomically'
finally:
 if DB.exists():DB.unlink()
verification['output_disposition']=disposition
verification['output_path']=str(DEST)
print(json.dumps(verification,ensure_ascii=False,indent=2))
