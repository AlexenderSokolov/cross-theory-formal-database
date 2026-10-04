"""Restore pinned schema1 compile-artifact archives into a fresh explicit final map.

Transport only: no network, Git, compilation, SQL, source admission or corpus counts.
The externally trusted helper pin is provided by the caller, never by an archive.
"""
from __future__ import annotations
import argparse,hashlib,io,json,shutil,stat,types,zipfile
from pathlib import Path,PurePosixPath
FORMAT='ordered schema1 validation archives with explicit final filemap'
DELIVERY='validation-artifact-delivery.json'
def digest(data):return hashlib.sha256(data).hexdigest()
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load_bytes(raw):
 def pairs(rows):
  result={}
  for k,v in rows:
   if k in result:raise ValueError('duplicate JSON key: '+k)
   result[k]=v
  return result
 return json.loads(raw.decode('utf8'),object_pairs_hook=pairs)
def load(path):return load_bytes(Path(path).read_bytes())
def dump(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def pin(value):
 if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):raise ValueError('SHA256 must be 64 lowercase hex characters')
 return value
def integer(value,label,minimum=0):
 if type(value) is not int or value<minimum:raise ValueError('invalid '+label)
 return value
def canonical(value):
 if not isinstance(value,str) or not value or any(ord(c)<32 for c in value) or ':' in value:raise ValueError('invalid relative path')
 p=PurePosixPath(value)
 if p.is_absolute() or '..' in p.parts or '\\' in value or p.as_posix()!=value or value=='.':raise ValueError('unsafe/noncanonical relative path')
 return p
def identifier(value):
 if not isinstance(value,str) or not value or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.' for c in value) or value in ('.','..') or not value[0].isalnum():raise ValueError('invalid archive identifier')
 return value
def artifact_path(value):
 p=canonical(value);parts=p.parts
 if len(parts)==3 and parts[0]=='build' and identifier(parts[1]) and Path(parts[2]).suffix in ('.pdf','.log','.fls','.aux','.out'):return p
 if len(parts)==2 and parts[0]=='receipts' and parts[1].endswith('.json') and identifier(parts[1][:-5]):return p
 raise ValueError('not a compile artifact path: '+value)
def no_symlink(path):
 p=Path(path).absolute()
 for x in [p,*p.parents]:
  if x.is_symlink():raise ValueError('symlink input/output component: '+str(x))
 return p
def ordinary(path):
 p=no_symlink(path)
 if not p.is_file() or not stat.S_ISREG(p.stat().st_mode) or p.stat().st_mode&0o7000:raise ValueError('ordinary file required: '+str(p))
 return p
def local(root,name):
 p=no_symlink(root.joinpath(*canonical(name).parts))
 if not p.resolve().is_relative_to(root.resolve()):raise ValueError('input escapes archive root')
 return ordinary(p)
def zip_regular(info):
 mode=stat.S_IFMT(info.external_attr>>16)
 if info.is_dir() or mode not in (0,stat.S_IFREG) or info.external_attr&0x10:raise ValueError('ZIP entry is not a regular file: '+info.filename)
def content_pin(value):
 if not isinstance(value,dict):raise ValueError('file pin must be an object')
 return {'sha256':pin(value.get('sha256')),'bytes':integer(value.get('bytes'),'file bytes')}
def ref(value):
 if not isinstance(value,dict) or set(value)!={'archive_id','sha256','bytes'}:raise ValueError('explicit archive/file identity required')
 return {'archive_id':identifier(value['archive_id']),**content_pin(value)}
def inspect_archive(root,d):
 if not isinstance(d,dict) or type(d.get('schema_version')) is not int or d['schema_version']!=1 or d.get('format')!='ordered zip parts with exact filemap':raise ValueError('schema1 descriptor required')
 parts=d.get('parts');count=integer(d.get('part_count'),'part_count',1)
 if not isinstance(parts,list) or len(parts)!=count or [p.get('index') for p in parts]!=list(range(count)):raise ValueError('invalid ordered parts')
 if d.get('build_root_relative')!='build' or d.get('receipt_set_relative')!='receipts':raise ValueError('unexpected schema1 build/receipt roots')
 paths=set();buffers=[];checked=[]
 for part in parts:
  integer(part.get('index'),'part index');name=canonical(part.get('path')).as_posix()
  if name in paths:raise ValueError('duplicate part path')
  paths.add(name);expected=content_pin(part);p=local(root,name);raw=p.read_bytes()
  if len(raw)!=expected['bytes'] or digest(raw)!=expected['sha256']:raise ValueError('part identity mismatch')
  buffers.append(raw);checked.append((p,expected))
 raw=b''.join(buffers)
 if len(raw)!=integer(d.get('archive_bytes'),'archive bytes',1) or digest(raw)!=pin(d.get('archive_sha256')):raise ValueError('archive identity mismatch')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  names=z.namelist()
  if len(names)!=len(set(names)):raise ValueError('duplicate ZIP paths')
  for info in z.infolist():zip_regular(info)
  fmap=load_bytes(z.read('ARTIFACT_FILEMAP.json'))
  if not isinstance(fmap,dict) or len(fmap)!=integer(d.get('file_count'),'file_count',1) or set(names)!=set(fmap)|{'ARTIFACT_FILEMAP.json'}:raise ValueError('ZIP filemap mismatch')
  checked_map={}
  for name,value in fmap.items():
   artifact_path(name);expected=content_pin(value);b=z.read(name)
   if len(b)!=expected['bytes'] or digest(b)!=expected['sha256']:raise ValueError('ZIP artifact identity mismatch')
   checked_map[name]=expected
 return checked_map,checked

def final_layout(fmap):
 groups={};receipts=set()
 for name in fmap:
  p=artifact_path(name)
  if p.parts[0]=='build':groups.setdefault(p.parts[1],set()).add(p.parts[2])
  else:receipts.add(p.parts[1][:-5])
 if not groups or set(groups)!=receipts:raise ValueError('final build and receipt ID coverage differs')
 for ident,names in groups.items():
  pdfs=[n for n in names if n.endswith('.pdf')]
  if len(pdfs)!=1:raise ValueError('one final compiled PDF required for '+ident)
  stem=pdfs[0][:-4];required={stem+ext for ext in ('.pdf','.log','.fls','.aux')}|{'compiler.log'}
  if not required.issubset(names) or not names.issubset(required|{stem+'.out'}):raise ValueError('incomplete/unknown final compile artifact set for '+ident)

def preflight(chain_path,expected_chain_sha256,archive_roots,helper_path,expected_helper_sha256,output):
 chain_path=ordinary(chain_path);helper_path=ordinary(helper_path);expected_chain_sha256=pin(expected_chain_sha256);expected_helper_sha256=pin(expected_helper_sha256)
 if sha(chain_path)!=expected_chain_sha256:raise ValueError('external chain pin mismatch')
 helper_bytes=helper_path.read_bytes()
 if digest(helper_bytes)!=expected_helper_sha256:raise ValueError('external trusted helper pin mismatch')
 doc=load(chain_path)
 if not isinstance(doc,dict) or type(doc.get('schema_version')) is not int or doc['schema_version']!=2 or doc.get('format')!=FORMAT:raise ValueError('schema2 chain required')
 records=doc.get('archives')
 if not isinstance(records,list) or not records or [r.get('index') for r in records]!=list(range(len(records))):raise ValueError('invalid ordered archives')
 roots={identifier(k):no_symlink(v) for k,v in archive_roots.items()};ids=[identifier(r.get('id')) for r in records]
 if len(ids)!=len(set(ids)) or set(ids)!=set(roots):raise ValueError('archive roots/IDs must match exactly once')
 output=no_symlink(output)
 if output.exists() or output.is_symlink():raise ValueError('output must be fresh; existing output preserved')
 for p in [chain_path,helper_path,*roots.values()]:
  if output.resolve().is_relative_to(p.resolve()) or p.resolve().is_relative_to(output.resolve()):raise ValueError('output overlaps immutable input')
 plans=[];all_paths={};descriptor_paths=set()
 for rec in records:
  integer(rec['index'],'archive index');root=roots[rec['id']]
  if not root.is_dir():raise ValueError('archive root must be a real directory')
  descriptor=local(root,DELIVERY)
  if descriptor in descriptor_paths:raise ValueError('same archive root declared twice')
  descriptor_paths.add(descriptor);h=pin(rec.get('delivery_sha256'))
  if sha(descriptor)!=h or load(descriptor)!=rec.get('delivery'):raise ValueError('schema1 descriptor pin/inline record mismatch')
  fmap,parts=inspect_archive(root,rec['delivery']);plans.append({'id':rec['id'],'index':rec['index'],'root':root,'descriptor':descriptor,'descriptor_sha256':h,'delivery':rec['delivery'],'filemap':fmap,'parts':parts})
  for name,value in fmap.items():all_paths.setdefault(name,[]).append({'archive_id':rec['id'],**value})
 final=doc.get('final_filemap');stage_only=doc.get('stage_only_paths',{})
 if not isinstance(final,dict) or not final or not isinstance(stage_only,dict) or len(final)!=integer(doc.get('final_file_count'),'final file count',1):raise ValueError('explicit complete final filemap required')
 if set(final)&set(stage_only) or set(final)|set(stage_only)!=set(all_paths):raise ValueError('final/stage-only paths do not account for all archived paths')
 for name,value in final.items():
  artifact_path(name);chosen={'archive_id':value.get('archive_id'),**content_pin(value)};chosen=ref(chosen)
  if chosen not in all_paths[name]:raise ValueError('final file does not match declared recovered archive')
  conflicts=[r for r in all_paths[name] if r['sha256']!=chosen['sha256'] or r['bytes']!=chosen['bytes']]
  declarations=value.get('overrides',[])
  if not isinstance(declarations,list):raise ValueError('overrides must be an explicit list')
  declared=[ref(x) for x in declarations]
  if len(declared)!=len({x['archive_id'] for x in declared}) or declared!=conflicts:raise ValueError('conflicting historical bytes require complete ordered explicit overrides')
 for name,declarations in stage_only.items():
  artifact_path(name)
  if not isinstance(declarations,list) or [ref(x) for x in declarations]!=all_paths[name]:raise ValueError('stage-only path identities incomplete')
 final_layout(final)
 return {'chain':chain_path,'chain_sha256':expected_chain_sha256,'helper':helper_path,'helper_sha256':expected_helper_sha256,'helper_bytes':helper_bytes,'plans':plans,'final':final,'stage_only':stage_only,'output':output}

def restore(chain_path,expected_chain_sha256,archive_roots,helper_path,expected_helper_sha256,output):
 plan=preflight(chain_path,expected_chain_sha256,archive_roots,helper_path,expected_helper_sha256,output)
 # Execute only the captured bytes matching the caller's separate trusted helper pin.
 helper=types.ModuleType('_pinned_schema1_restore');helper.__file__=str(plan['helper']);exec(compile(plan['helper_bytes'],str(plan['helper']),'exec'),helper.__dict__)
 if not callable(getattr(helper,'restore',None)):raise ValueError('trusted helper has no restore(root,destination) interface')
 out=plan['output'];out.mkdir(parents=True);stages={};results=[]
 try:
  for rec in plan['plans']:
   if sha(rec['descriptor'])!=rec['descriptor_sha256']:raise ValueError('descriptor changed after preflight')
   stage=out/'stages'/f"{rec['index']:05}-{rec['id']}";result=helper.restore(rec['root'],stage);actual={p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file()}
   if actual!=set(rec['filemap'])|{'RESTORE_RECEIPT.json'}:raise ValueError('schema1 restored stage inventory differs')
   for name,value in rec['filemap'].items():
    p=local(stage,name)
    if p.stat().st_size!=value['bytes'] or sha(p)!=value['sha256']:raise ValueError('schema1 restored stage bytes differ')
   stages[rec['id']]=stage;results.append({'index':rec['index'],'id':rec['id'],'delivery_sha256':rec['descriptor_sha256'],'archive_sha256':rec['delivery']['archive_sha256'],'stage':str(stage),'actual_schema1_restore':result})
  for name,value in plan['final'].items():
   source=local(stages[value['archive_id']],name);target=out.joinpath(*canonical(name).parts);target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists() or target.is_symlink():raise ValueError('unexpected final target exists')
   shutil.copyfile(source,target);target.chmod(0o644)
   if target.stat().st_size!=value['bytes'] or sha(target)!=value['sha256']:raise ValueError('final artifact bytes differ')
  for rec in plan['plans']:
   if sha(rec['descriptor'])!=rec['descriptor_sha256']:raise ValueError('input descriptor changed during restoration')
   for p,value in rec['parts']:
    ordinary(p)
    if p.stat().st_size!=value['bytes'] or sha(p)!=value['sha256']:raise ValueError('input part changed during restoration')
  if sha(ordinary(plan['helper']))!=plan['helper_sha256'] or sha(ordinary(plan['chain']))!=plan['chain_sha256']:raise ValueError('helper/chain changed during restoration')
  result={'schema_version':2,'status':'actual_validation_chain_restore_complete_not_qualified_or_remote','chain_sha256':plan['chain_sha256'],'externally_trusted_schema1_helper_sha256':plan['helper_sha256'],'destination':str(out),'build_root':str(out/'build'),'receipt_root':str(out/'receipts'),'artifact_files':len(plan['final']),'archives':results,'final_filemap':plan['final'],'stage_only_paths':plan['stage_only'],'inputs_unchanged_and_all_history_stages_retained':True,'new_compile':False,'qualified_count_increment':0,'remote_count_increment':0}
  dump(out/'CHAIN_RESTORE_RECEIPT.json',result);return result
 except Exception as exc:
  dump(out/'CHAIN_RESTORE_FAILED.json',{'status':'failed_partial_output_preserved','error':str(exc),'chain_sha256':plan['chain_sha256'],'inputs_not_modified_by_this_tool':True,'completed_stages':results});raise

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--chain',required=True,type=Path);p.add_argument('--expected-chain-sha256',required=True);p.add_argument('--archive-root',required=True,action='append',metavar='ID=LOCAL_DIRECTORY');p.add_argument('--schema1-helper',required=True,type=Path);p.add_argument('--expected-helper-sha256',required=True);p.add_argument('--output',required=True,type=Path);a=p.parse_args();roots={}
 for value in a.archive_root:
  ident,sep,path=value.partition('=')
  if not sep or not path or ident in roots:p.error('each archive root must be a unique ID=LOCAL_DIRECTORY')
  roots[identifier(ident)]=Path(path)
 print(json.dumps(restore(a.chain,a.expected_chain_sha256,roots,a.schema1_helper,a.expected_helper_sha256,a.output),ensure_ascii=False,indent=2))
if __name__=='__main__':main()