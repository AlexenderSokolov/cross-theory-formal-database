import pathlib,json,re,sys
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';sys.path.insert(0,str(P.parents[1]/'corpus-work/scripts'));import prepared_delivery as d
load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=O/'AGP-stacks-0FU4/task.json';t=load(p)
for s in t['context_spans']+t['assembly']['body_spans']:
 if s['start_line']==5376 and s['end_line']==5405:s['end_line']=5416
body='\n'.join('\n'.join((P/s['path']).read_text(encoding='utf8').splitlines()[s['start_line']-1:s['end_line']]) for s in t['assembly']['body_spans']);labels=set(re.findall(r'\\label\{([^}]+)\}',body));t['assembly']['external_references']=[x for x in t['assembly']['external_references'] if x['label'] not in labels]
save(p,t);rp=O/'AGP-stacks-0FU4/focused-review.json';r=load(rp);r['context_spans']=t['context_spans'];r['non_load_bearing_references']=[x['label'] for x in t['assembly']['external_references']];r['approved_task_config']=d.task_config(t);save(rp,r)
