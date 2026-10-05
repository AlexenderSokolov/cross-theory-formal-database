"""Copy only the prepared public list into Git; preserve all historical files."""
from pathlib import Path
import argparse,json,os,shutil,subprocess,tempfile

def stage(batch):
 batch=Path(batch).resolve();info=json.loads((batch/'batch.json').read_text())
 release=batch/'release';prep=json.loads((release/'release-preparation.json').read_text())
 if prep['status']!='prepared_editable_release_not_restored_or_remote_verified' or prep['items']!=info['expected_count']:raise ValueError('prepared release required')
 B=Path('/disks/sata1/yupeng/human-proof-corpus');repo=B/'repo'
 publication=json.loads((release/'PUBLIC_FILELIST.json').read_text());paths=[]
 if any(x['path']=='RECOVERY_CURRENT.md' for x in publication['files']):raise ValueError('exclude inherited recovery instructions from the prepared list before publishing')
 for row in publication['files']:
  rel=Path(row['path'])
  if rel.is_absolute() or '..' in rel.parts:raise ValueError('invalid prepared public path')
  source=release/'package'/rel;dest=repo/'editable-corpus'/rel
  dest.parent.mkdir(parents=True,exist_ok=True)
  # Replace a target inode, never modify a possibly shared hardlink in place.
  with tempfile.NamedTemporaryFile(dir=dest.parent,delete=False) as out:
   with source.open('rb') as stream:shutil.copyfileobj(stream,out)
   temporary=out.name
  os.replace(temporary,dest);paths.append('editable-corpus/'+rel.as_posix())
 handoff=repo/'handoff/yupeng'/('main'+str(info['expected_count']));handoff.mkdir(exist_ok=True)
 for source in (release/'PUBLIC_FILELIST.json',batch/'merge/batch-result.json',batch/'material-review.json'):
  dest=handoff/source.name;shutil.copyfile(source,dest);paths.append(dest.relative_to(repo).as_posix())
 doc=repo/'editable-corpus/RECOVERY_CURRENT.md'
 doc.write_text(f'''# {info['expected_count']}题主库恢复

正文、INDEX与全文SQLite的当前版本以本目录manifest及database-delivery.json为准。
历史文件保留；只恢复当前描述中列出的分段，不把旧备份再次计数。

```sh
python3 restore_database.py
python3 restore_validation_artifacts.py --destination /absolute/new/artifacts
```

然后显式执行当前仓库corpus-work/scripts/validate_corpus.py --mode editable-delivery，传入实际package、delivery-evidence、恢复后的build和receipts及独立report。公开恢复成功后才更新交付数。当前组批使用一次主库重建和一次aggregate；合格题证的历史真实编译按不变输入复用。
''')
 paths.append('editable-corpus/RECOVERY_CURRENT.md')
 paths.append('handoff/yupeng/PRODUCTION_QUEUE.json')
 for index in range(0,len(paths),200):subprocess.run(['git','-C',str(repo),'add','--',*paths[index:index+200]],check=True)
 result={'status':'explicit_prepared_files_staged_not_pushed','count':info['expected_count'],'paths':paths}
 (batch/'git-staging.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'count':result['count'],'files':len(paths)}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('batch');stage(p.parse_args().batch)
