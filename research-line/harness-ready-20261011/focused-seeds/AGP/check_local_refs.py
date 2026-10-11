import json,pathlib
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011')
for x in json.loads((P/'focused-seeds/AGP/READY_TASKS.json').read_text(encoding='utf8')):
 if not x['task_id'].startswith('AGP-stacks'):continue
 t=json.loads((P/x['task_path']).read_text(encoding='utf8'));print(t['task_id']);print([z['label'] for z in t['assembly']['external_references'] if not z['label'].startswith(('algebra-','sites-','categories-','coherent-','homology-','chow-','morphisms-','divisors-','formal-spaces-','descent-','more-algebra-','simplicial-','perfect-','pic-','groupoids-','bootstrap-','restricted-','sites-cohomology-'))])
