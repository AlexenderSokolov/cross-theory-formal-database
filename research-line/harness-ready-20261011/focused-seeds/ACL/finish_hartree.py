import pathlib,json,sys
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');r=p.parent.parent;tid='ACL-analysis-hartree-low-regularity-asymptotic-stability';f=p/'focused-seeds/ACL'/tid/'task.json';t=json.loads(f.read_text(encoding='utf-8'))
for collection in [t['statement_spans'],t['proof_spans'],t['context_spans'],t['assembly']['preamble_spans'],t['assembly']['body_spans']]:
 for s in collection:
  if s['path'].replace('\\','/')=='focused-seeds/ACL/sources/analysis-cache-820/source.tex':s['path']='focused-seeds/ACL/sources/analysis-cache-820/source-layout.tex'
f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');sys.path.insert(0,str(r/'corpus-work/scripts'));import prepared_delivery as pd
pd.assemble(f,p,r/'materials',compile_now=False,material_only=True,refresh=True);q=pd.compile_job(r/'materials'/tid/'r001',resume=True);print(q['status'],q['pages'])