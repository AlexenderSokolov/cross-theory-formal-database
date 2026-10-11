import pathlib,json
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011/focused-seeds/AGP')
for name in ['AGP-sigma2020-112-yangian-center/task.json','AGP-sigma2020-112-yangian-center/focused-review.json','SOURCE_RECORDS.json','prepare_yangian_center.py']:
 p=P/name;s=p.read_text(encoding='utf8');p.write_text(s.replace('Theorem3.5','Theorem3.6'),encoding='utf8')
p=P/'sources/stacks-snapshot-20261011/LICENSE_OBSERVATION.json';r=json.loads(p.read_text(encoding='utf8'));r['status']='supported';p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
