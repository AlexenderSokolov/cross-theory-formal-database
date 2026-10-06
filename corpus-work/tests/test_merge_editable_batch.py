"""Synthetic engineering fixtures only; these are never corpus candidates."""
import json
import tempfile
import unittest
from pathlib import Path
import sys
import os
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import merge_editable_packages as merge
import merge_editable_batch as batch

class MergeContract(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='merge-contract-fixture-', dir=os.environ.get('MERGE_TEST_ROOT')))
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


class AddedSingleGuards(unittest.TestCase):
    setUp = MergeContract.setUp
    make = MergeContract.make
    change = MergeContract.change
    run_merge = MergeContract.run_merge

    def test_claim_alias_duplicate_refused(self):
        self.change(self.incoming, lambda m,e:e['items']['002'].update(historical_claim_key_aliases=[' CLAIM-A ']))
        with self.assertRaisesRegex(ValueError, 'duplicate claim'): self.run_merge()

    def test_derived_top_level_preparation_rebuilt_and_inputs_preserved(self):
        a=self.base/'merge-preparation.json';b=self.incoming/'merge-preparation.json'
        merge.dump(a,{'old':'base'});merge.dump(b,{'old':'incoming'})
        before=[merge.sha(a),merge.sha(b)]
        receipt=self.run_merge()
        self.assertEqual(receipt['items'],2)
        self.assertEqual([merge.sha(a),merge.sha(b)],before)
        prepared=json.loads((self.root/'output/merge-preparation.json').read_text())
        self.assertEqual(prepared['base_items'],1);self.assertEqual(prepared['incoming_items'],1)
        self.assertNotIn('old',prepared)

    def test_nested_manifest_duplicate_key_refused(self):
        p=self.incoming/'manifest.json';p.write_text(p.read_text().replace('"status": "verified_editable_tex"','"status":"pending","status": "verified_editable_tex"'))
        e=json.loads((self.incoming/'delivery-evidence.json').read_text());e['package_manifest_sha256']=merge.sha(p);merge.dump(self.incoming/'delivery-evidence.json',e)
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):self.run_merge()

    def test_single_dangling_output_preserved(self):
        out=self.root/'output';target=self.root/'nonexistent';out.symlink_to(target,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'output must be new'):self.run_merge()
        self.assertTrue(out.is_symlink());self.assertFalse(target.exists())

class BatchPreflightGuards(unittest.TestCase):
    setUp = MergeContract.setUp
    make = MergeContract.make
    change = MergeContract.change

    def reviewed(self):
        master=self.root/'master';master.mkdir(exist_ok=True)
        for name in batch.HELPERS:(master/name).write_text('SYNTHETIC FIXED HELPER ONLY\\n')
        for pkg in [self.base,self.incoming]:(pkg/'schema.sql').write_bytes((master/'schema.sql').read_bytes())
        entries=[];artifacts=[]
        for n,pkg in enumerate([self.base,self.incoming]):
            b=self.root/('build'+str(n));b.mkdir(exist_ok=True);(b/'artifact.stub').write_text('SYNTHETIC COMPILE FILE; NOT VALID DELIVERY')
            r=self.root/('receipts'+str(n));r.mkdir(exist_ok=True);(r/'receipt.stub').write_text('SYNTHETIC RECEIPT')
            entries.append({'package':str(pkg),'manifest_sha256':merge.sha(pkg/'manifest.json'),'build_root':str(b),'receipt_root':str(r)})
            artifacts.append({'build':batch.filemap(b),'receipts':batch.filemap(r)})
        launcher=self.root/'launcher';launcher.write_text('SYNTHETIC LAUNCHER NOT EXECUTED')
        spec={'base':entries[0],'incoming':[entries[1]],'master_helpers':str(master),'compile_launcher':str(launcher)}
        programmes={name:merge.sha(p) for name,p in batch.programme_paths().items()};programmes['compile_launcher']=merge.sha(launcher)
        review={'schema_version':1,'status':'material_review_complete','holds':[],'duplicates':[],
            'basis':'SYNTHETIC ENGINEERING FIXTURES ONLY; not corpus admission.','compile_reuse_basis':'SYNTHETIC FILEMAP TEST, no real compile claimed.',
            'base_manifest_sha256':entries[0]['manifest_sha256'],'incoming_manifest_sha256':[entries[1]['manifest_sha256']],
            'incoming_ids':[x['problem_id'] for x in json.loads((self.incoming/'manifest.json').read_text())['items']],
            'reviewed_filemaps':{'base':batch.filemap(self.base),'incoming':[batch.filemap(self.incoming)]},
            'reviewed_artifact_filemaps':{'base':artifacts[0],'incoming':[artifacts[1]]},
            'programme_sha256':programmes,'master_helper_sha256':{name:merge.sha(master/name) for name in batch.HELPERS}}
        return spec,review

    def check(self):
        spec,review=self.reviewed()
        return batch.preflight(spec,review,self.root/'out')

    def test_reviewed_preflight_never_qualifies_or_writes(self):
        self.check();self.assertFalse((self.root/'out').exists())

    def test_duplicate_id_refused_before_output(self):
        def edit(m,e):
            m['items'][0]['problem_id']='001';e['items']['001']=e['items'].pop('002')
        self.change(self.incoming,edit)
        (self.incoming/'INDEX.md').write_text((self.incoming/'INDEX.md').read_text().replace('| 002 |','| 001 |'))
        with self.assertRaisesRegex(ValueError,'duplicate stable ID'):self.check()
        self.assertFalse((self.root/'out').exists())

    def test_duplicate_claim_refused_before_output(self):
        self.change(self.incoming,lambda m,e:e['items']['002'].update(claim_key='claim-a'))
        with self.assertRaisesRegex(ValueError,'duplicate claim'):self.check()

    def test_source_conflict_refused_before_output(self):
        self.change(self.incoming,lambda m,e:m['items'][0].update(source_id='source-a',author='Wrong author'))
        with self.assertRaisesRegex(ValueError,'source identity conflict'):self.check()

    def test_missing_asset_refused_before_output(self):
        self.change(self.incoming,lambda m,e:m['items'][0].update(asset_dependencies=[{'path':'absent.pdf','sha256':'0'*64}]))
        with self.assertRaisesRegex(ValueError,'missing/changed asset'):self.check()

    def test_existing_output_preserved(self):
        out=self.root/'out';out.mkdir();(out/'owner').write_text('preserve')
        with self.assertRaisesRegex(ValueError,'output must be new'):self.check()
        self.assertEqual((out/'owner').read_text(),'preserve')

    def test_batch_dangling_output_preserved(self):
        out=self.root/'out';target=self.root/'dangling-target';out.symlink_to(target,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'output must be new'):self.check()
        self.assertTrue(out.is_symlink());self.assertFalse(target.exists())

    def test_batch_deep_duplicate_json_rejected(self):
        p=self.root/'duplicate-spec.json';p.write_text('{"base":{"nested":{"key":1,"key":2}}}')
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):batch.load(p)

    def test_incomplete_external_review_refused(self):
        spec,review=self.reviewed();review['basis']=''
        with self.assertRaisesRegex(ValueError,'explicit complete external'):batch.preflight(spec,review,self.root/'out')

    def test_helper_pin_drift_refused(self):
        spec,review=self.reviewed();review['master_helper_sha256']['rebuild_database.py']='0'*64
        with self.assertRaisesRegex(ValueError,'fixed master helper identity'):batch.preflight(spec,review,self.root/'out')

    def test_immutable_artifact_reuse_same_filesystem(self):
        source=self.root/'artifact';source.write_text('immutable');target=self.root/'reuse'
        mode=source.stat().st_mode;batch.reuse_immutable(source,target)
        self.assertEqual(source.stat().st_ino,target.stat().st_ino)
        self.assertEqual(source.read_bytes(),target.read_bytes());self.assertEqual(source.stat().st_mode,mode)

if __name__=='__main__':unittest.main()
