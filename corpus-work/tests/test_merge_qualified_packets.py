"""Synthetic engineering fixtures only; these are never corpus candidates."""
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import merge_qualified_packets as merge

class MergeContract(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='merge-contract-fixture-'))
        self.base=self.make('base','001','claim-a','source-a')
        self.incoming=self.make('incoming','002','claim-b','source-b')
        self.rebuild=self.root/'fixture_rebuild.py'
        self.rebuild.write_text("def rebuild(root, output):\n output.write_bytes(b'TEST DATABASE, NOT CORPUS')\n return 2\n")

    def make(self,name,ident,claim,sid):
        root=self.root/name;root.mkdir()
        body=root/'items'/f'{ident}.tex';body.parent.mkdir();body.write_text('SYNTHETIC TEST FIXTURE ONLY\n')
        (root/'license.txt').write_text('TEST FIXTURE ONLY')
        (root/'receipt.json').write_text('{}')
        row={'problem_id':ident,'title':'Fixture','status':'verified_editable_tex',
             'item_path':f'items/{ident}.tex','tex_sha256':merge.sha(body),
             'source_id':sid,'author':'Fixture','work':'Fixture','source_url':'https://example.invalid/fixture',
             'source_version':'FIXTURE','retrieved_at':'2000-01-01','license':'FIXTURE',
             'license_path':'license.txt','compile_receipt':'receipt.json','difficulty_level':'H1',
             'difficulty_reason':'TEST FIXTURE ONLY','asset_dependencies':[]}
        merge.dump(root/'manifest.json',{'items':[row]})
        (root/'INDEX.md').write_text(f"| {ident} | Fixture | H1 | [body](items/{ident}.tex) | [original](https://stacks.math.columbia.edu/tag/01XF) |\n")
        merge.dump(root/'delivery-evidence.json',{'items':{ident:{'claim_key':claim,'item_sha256':row['tex_sha256'],'independent_problem_unit':True,'bodies':[{'fixture':True}],'sources':[{'fixture':True}]}},'package_manifest_sha256':merge.sha(root/'manifest.json')})
        return root

    def change(self,root,callback):
        m=json.loads((root/'manifest.json').read_text());e=json.loads((root/'delivery-evidence.json').read_text())
        callback(m,e);merge.dump(root/'manifest.json',m);e['package_manifest_sha256']=merge.sha(root/'manifest.json');merge.dump(root/'delivery-evidence.json',e)

    def run_merge(self, omit_extra=False):
        review=self.root/'review.json'
        merge.dump(review,{'status':'material_review_complete','incoming_ids':[x['problem_id'] for x in json.loads((self.incoming/'manifest.json').read_text())['items']],
                           'base_manifest_sha256':merge.sha(self.base/'manifest.json'),'incoming_manifest_sha256':merge.sha(self.incoming/'manifest.json'),'holds':[],'duplicates':[],
                           'reviewed_filemaps':{key:{p.relative_to(root).as_posix():merge.sha(p) for p in root.rglob('*') if p.is_file() and not (omit_extra and p.name=='unreviewed.html')} for key,root in [('base',self.base),('incoming',self.incoming)]}})
        return merge.merge_packets(self.base,self.incoming,self.root/'output',self.rebuild,merge.sha(self.base/'manifest.json'),merge.sha(self.incoming/'manifest.json'),review)

    def test_duplicate_id_refused_and_base_unchanged(self):
        before=merge.sha(self.base/'manifest.json')
        def edit(m,e):
            row=m['items'][0];old=row['problem_id'];row['problem_id']='001';e['items']['001']=e['items'].pop(old)
        self.change(self.incoming,edit)
        with self.assertRaisesRegex(ValueError,'duplicate stable ID'):self.run_merge()
        self.assertEqual(before,merge.sha(self.base/'manifest.json'));self.assertFalse((self.root/'output').exists())

    def test_same_claim_different_id_refused(self):
        self.change(self.incoming,lambda m,e:e['items']['002'].update(claim_key='claim-a'))
        with self.assertRaisesRegex(ValueError,'duplicate claim'):self.run_merge()

    def test_normalized_claim_duplicate_refused(self):
        self.change(self.incoming,lambda m,e:e['items']['002'].update(claim_key='  CLAIM-A  '))
        with self.assertRaisesRegex(ValueError,'duplicate claim'):self.run_merge()

    def test_unreviewed_extra_file_refused(self):
        (self.incoming/'unreviewed.html').write_text('unapproved input')
        with self.assertRaisesRegex(ValueError,'unreviewed/missing package file'):self.run_merge(omit_extra=True)

    def test_source_metadata_conflict_refused(self):
        self.change(self.incoming,lambda m,e:m['items'][0].update(source_id='source-a',author='Wrong author'))
        with self.assertRaisesRegex(ValueError,'source identity conflict'):self.run_merge()

    def test_missing_core_witness_refused(self):
        self.change(self.incoming,lambda m,e:e['items']['002'].update(bodies=[]))
        with self.assertRaisesRegex(ValueError,'missing body/source'):self.run_merge()

    def test_missing_asset_refused(self):
        self.change(self.incoming,lambda m,e:m['items'][0].update(asset_dependencies=[{'path':'absent.pdf','sha256':'0'*64}]))
        with self.assertRaisesRegex(ValueError,'missing/changed asset'):self.run_merge()

    def test_existing_output_preserved(self):
        out=self.root/'output';out.mkdir();(out/'owner.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError,'output must be new'):self.run_merge()
        self.assertEqual('keep',(out/'owner.txt').read_text())

    def test_wrong_manifest_binding_refused(self):
        e=json.loads((self.incoming/'delivery-evidence.json').read_text());e['package_manifest_sha256']='0'*64;merge.dump(self.incoming/'delivery-evidence.json',e)
        with self.assertRaisesRegex(ValueError,'does not bind'):self.run_merge()

    def test_positive_union_still_not_admitted(self):
        receipt=self.run_merge()
        self.assertEqual(receipt['items'],2)
        self.assertEqual(receipt['status'],'prepared_not_fresh_validated_or_published')
        output=self.root/'output';self.assertTrue((output/'items/001.tex').exists());self.assertTrue((output/'items/002.tex').exists())
        evidence=json.loads((output/'delivery-evidence.json').read_text());self.assertEqual(evidence['package_manifest_sha256'],merge.sha(output/'manifest.json'))
        self.assertIn('https://stacks.math.columbia.edu/tag/01XF',(output/'INDEX.md').read_text())

if __name__=='__main__':unittest.main()
