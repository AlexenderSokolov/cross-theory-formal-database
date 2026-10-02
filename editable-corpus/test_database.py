import hashlib,json,sqlite3,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
class DatabaseTests(unittest.TestCase):
 def test_full_tex_content_and_rebuild(self):
  with tempfile.TemporaryDirectory() as tmp:
   a=Path(tmp)/'a.sqlite';b=Path(tmp)/'b.sqlite';r=subprocess.run(['python3',str(ROOT/'rebuild_database.py'),'--output',str(a)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
   manifest=json.loads((ROOT/'manifest.json').read_text());db=sqlite3.connect(a);self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok');self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(),[])
   rows=db.execute('SELECT problem_id,tex_path,tex_content,tex_sha256 FROM problems ORDER BY problem_id').fetchall();self.assertEqual(len(rows),len(manifest['items']))
   for i,p,c,h in rows:self.assertEqual(c,(ROOT/p).read_text());self.assertEqual(h,hashlib.sha256(c.encode()).hexdigest());self.assertIn(r'\begin{document}',c);self.assertIn(r'\end{document}',c);self.assertNotIn(r'\includepdf',c)
   self.assertEqual(len({r[0] for r in rows}),len(rows));self.assertEqual(db.execute('SELECT DISTINCT status FROM problems').fetchall(),[('verified_editable_tex',)])
   for row in manifest['items']:self.assertEqual(db.execute('SELECT source_id FROM problems WHERE problem_id=?',(row['problem_id'],)).fetchone()[0],row['source_id'])
   db.close();subprocess.run(['python3',str(ROOT/'rebuild_database.py'),'--output',str(b)],check=True,capture_output=True);self.assertEqual(a.read_bytes(),b.read_bytes())
if __name__=='__main__':unittest.main()
