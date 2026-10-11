import json,pathlib,re
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011')
R=P.parents[1]
def load(p):return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
m=load(R/'editable-corpus/manifest.json');print(type(m).__name__, list(m)[:15] if isinstance(m,dict) else len(m))
c=load(R/'editable-corpus/catalog.json');print(type(c).__name__,list(c)[:15] if isinstance(c,dict) else len(c))
p=load(P/'scouting/geometry/followup_leads.json');print(json.dumps([(x.get('title'),x.get('cached_source_candidates')) for x in p['leads']],ensure_ascii=False))
