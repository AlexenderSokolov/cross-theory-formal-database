"""Rebuild the full-text SQLite corpus from manifest.json and published TeX files."""
import argparse,hashlib,json,sqlite3
from pathlib import Path

def rebuild(root,output):
 manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'));temporary=output.with_suffix(output.suffix+'.tmp')
 if temporary.exists():temporary.unlink()
 db=sqlite3.connect(temporary)
 try:
  db.executescript((root/'schema.sql').read_text(encoding='utf-8'));sources={}
  for item in sorted(manifest['items'],key=lambda x:x['problem_id']):
   assert item['status']=='verified_editable_tex';content=(root/item['item_path']).read_text(encoding='utf-8');assert hashlib.sha256(content.encode()).hexdigest()==item['tex_sha256']
   receipt=json.loads((root/item['compile_receipt']).read_text());assert receipt['ok'] is True and receipt['passes']==2 and receipt['input_sha256']==item['tex_sha256']
   sid=item['source_id'];source=tuple(item[k] for k in ('author','work','source_url','source_version','retrieved_at','license','license_path'))
   if sid not in sources:db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)',(sid,)+source);sources[sid]=source
   else:assert sources[sid]==source
   db.execute('INSERT INTO problems VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(item['problem_id'],item['title'],item['difficulty_level'],item['difficulty_reason'],sid,json.dumps({'primary':item['primary'],'contexts':item['contexts']},sort_keys=True,ensure_ascii=False),item['item_path'],content,item['tex_sha256'],item['origin_class'],item['status'],item['compile_receipt']))
  db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not db.execute('PRAGMA foreign_key_check').fetchall();assert db.execute('SELECT COUNT(*) FROM problems').fetchone()[0]==len(manifest['items']);db.execute('VACUUM')
 finally:db.close()
 temporary.replace(output);return len(manifest['items'])
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path);args=parser.parse_args();root=Path(__file__).resolve().parent;print('Rebuilt',rebuild(root,args.output or root/'corpus.sqlite'),'full-text problem records')
