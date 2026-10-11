import pathlib,json,re
R=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010')
for s in (R/'research-line/scale-30000-20261010/resources/old-review-priority.jsonl').read_text(encoding='utf-8-sig').splitlines():
 x=json.loads(s)
 if not x.get('reuse_route','').startswith('positive_H2'):continue
 if re.search('probab|Markov|random|martingale|chaos|Brownian|mixing|percolation',x.get('work',''),re.I):print(x['problem_id'],x['work'],x.get('current_primary_locator'),x.get('historical_reason','')[:600])
