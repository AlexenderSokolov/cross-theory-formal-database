"""Prepare cached block inputs; dry-run by default, never launch a worker."""
import argparse
import copy
import json
import shutil
from pathlib import Path

B = Path('/disks/sata1/yupeng/human-proof-corpus')
INHERITED = {'r003':['2325','2326','2368','2375','2378'],
             'r004':['2316','2374','2385','2509','2540'],
             'r005':['2510','2512','2524']}
EXCLUDED = {'1791','2244','2282','2254','1907','1793','2286','2415','1794','1797'}
ASSETS = {'cached_published_PDF':'source.pdf', 'cached_publisher_native_TeX':'source0.tex',
          'cached_article_license_page':'article-license.html'}

def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))

def plan(root):
    root=Path(root).resolve();state=root/'operations/corpusctl'
    q=load(root/'repo/handoff/yupeng/PRODUCTION_QUEUE.json')
    master=load(Path(q['base']['package'])/'manifest.json')
    catalog={r['problem_id']:r for line in (root/'repo/handoff/catalog/candidate_catalog.jsonl').read_text().splitlines() if line.strip() for r in [json.loads(line)]}
    inventory_path=root/'reports/published-pilot/cached-next-blocks-r001/safe-source-inventory-r003.json'
    inventory=load(inventory_path)['catalog_order_unclaimed_cached_PDF_native_CC_BY_entries']
    packets=[];blocks=[];reserved=set(EXCLUDED)|{str(x['problem_id']) for x in master['items']}|{str(x['problem_id']) for x in q['queued_new_root_admitted']}
    works=set();catalog_holds={i for i,r in catalog.items() if r.get('current_hold')}
    holdpath=state/'source-holds.json'
    if holdpath.exists():reserved.update(load(holdpath))
    reserved.update(catalog_holds)
    for suffix,ids in INHERITED.items():
        blockroot=root/'candidates'/('native-source-continuous-'+suffix)
        handoff=load(blockroot/'HANDOFF_STOPPED.json')
        recorded={u['problem_id'] for u in handoff.get('items',handoff.get('units',[]))}
        units=[]
        for ident in ids:
            if ident in reserved or ident not in recorded:raise ValueError('inherited scope conflicts with current queue/hold/handoff: '+ident)
            packet=blockroot/ident/'SOURCE_PACKET.json';data=load(packet)
            if data['existing_id']!=ident:raise ValueError('inherited packet identity mismatch')
            for name in ('source.pdf','source0.tex'):
                if not (blockroot/ident/'cached-originals'/name).is_file():raise ValueError('inherited originals missing: '+ident+'/'+name)
            key=data['work_key']
            if key in works:raise ValueError('inherited work crosses block boundary: '+key)
            units.append(dict(problem_id=ident,work_key=key,source_packet=str(packet),workspace=str(blockroot/ident)))
        works.update(u['work_key'] for u in units);reserved.update(ids)
        blocks.append(dict(block_id='inherited-'+suffix,enabled=True,units=units,next_block_id='cached-next-'+suffix))
    # Keep the inventory's recorded order; one work is assigned to only one chain.
    main_ids={str(x['problem_id']) for x in master['items']}|{str(x['problem_id']) for x in q['queued_new_root_admitted']}
    unavailable_works={catalog[i].get('work_identity_key') for i in main_ids if i in catalog}
    remaining=[];unstable=[]
    for row in inventory:
        key=row['work_key']
        if key in works or key in unavailable_works:continue
        ids=[i for i in row.get('existing_catalog_candidate_ids',[]) if i not in reserved and i not in row.get('existing_local_held_candidate_ids_not_for_reselection',[])]
        if not ids:continue
        unstable.extend(i for i in ids if not isinstance(i,str) or not i.isdecimal() or i not in catalog)
        ids=[i for i in ids if isinstance(i,str) and i.isdecimal() and i in catalog]
        if not ids:continue
        objects={k:Path(row[k]['object_ref']) for k in ASSETS}
        if any(not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root) for p in objects.values()):continue
        remaining.append((row,ids,objects))
    counts={};cursor=0
    for suffix in INHERITED:
        units=[]
        while cursor<len(remaining) and len(units)<10:
            row,ids,objects=remaining[cursor];cursor+=1
            # Do not split one work between blocks; leave excess same-work candidates unassigned.
            selected=ids[:10-len(units)];works.add(row['work_key'])
            for ident in selected:
                location=root/'candidates/source-pipeline-v2'/suffix/ident
                data=dict(existing_id=ident,work_key=row['work_key'],title=row.get('work_title'),author=row.get('author'),
                          catalog_ordinal=catalog[ident].get('catalog_ordinal',row['catalog_first_ordinal']),
                          catalog_record=catalog[ident],inventory_reference=str(inventory_path),inventory_entry=copy.deepcopy(row),
                          source_object_paths={k:str(v) for k,v in objects.items()},article_url=row.get('article_url'),
                          cached_individual_CC_BY4_witness=row.get('cached_individual_CC_BY4_witness'),
                          candidate_status='unadmitted_cached_candidate_no_mathematical_qualification',
                          external_asset_or_input_hints=row.get('external_asset_or_input_lexical_hints',[]))
                packets.append((location,data,objects));units.append(dict(problem_id=ident,work_key=row['work_key'],source_packet=str(location/'SOURCE_PACKET.json'),workspace=str(location)))
            reserved.update(ids)
        counts[suffix]=len(units)
        if units:blocks.append(dict(block_id='cached-next-'+suffix,enabled=True,units=units,next_block_id=None))
        else:next(b for b in blocks if b['block_id']=='inherited-'+suffix)['next_block_id']=None
    flow=dict(schema_version=2,record_type='flow',flow_id='local-controller-cached-v2',blocks=blocks,initial_worker_slots=3,max_worker_slots=8,review_backlog_limit=25)
    old=load(root/'candidates/native-source-continuous-r002/executor-1-r002/RUNTIME_JOB.json')
    argv=list(old['argv'])
    argv[argv.index('--model')+1]='gpt-6.1-sol'
    for n,v in enumerate(argv):
        if v.startswith('model_reasoning_effort='):argv[n]='model_reasoning_effort="medium"'
    argv[argv.index('-C')+1]='{workspace}';argv[argv.index('-o')+1]='{result_path}.FINAL.txt'
    argv[-1:-1]=['--add-dir',str(state/'jobs')]
    command=dict(argv=argv,task_file=str(root/'repo/corpus-work/scripts/SOURCE_WORKER_TASK.md'))
    return flow,command,packets,dict(inherited=13,successor_counts=counts,next_candidate_count=sum(counts.values()),unstable_candidate_keys_skipped=unstable,selected_ids={b['block_id']:[u['problem_id'] for u in b['units']] for b in blocks},model='gpt-6.1-sol',effort='medium',production_started=False)

def apply(root,flow,command,packets,owner,generation):
    from corpus_control_protocol import controller_guard,save_json
    root=Path(root);state=root/'operations/corpusctl'
    with controller_guard(state,owner,generation):
        if not Path(command['task_file']).is_file():raise ValueError('deploy SOURCE_WORKER_TASK.md before apply')
        # Re-evaluate current authoritative state under the lock before any writes.
        actual=plan(root)
        if (actual[0],actual[1])!=(flow,command):raise ValueError('state changed since preview')
        for name,value in [('FLOW.json',flow),('worker-command.json',command)]:
            path=state/name
            if path.exists() and load(path)!=value:raise ValueError('preserve existing different '+name+'; explicit root reconciliation required')
        for location,data,objects in packets:
            target=location/'SOURCE_PACKET.json'
            if target.exists() and load(target)!=data:raise ValueError('candidate input changed; preserve existing packet')
            for key,name in ASSETS.items():
                destination=location/'cached-originals'/name
                if destination.exists() and not __import__('filecmp').cmp(objects[key],destination,shallow=False):raise ValueError('existing original differs')
        for location,data,objects in packets:
            originals=location/'cached-originals';originals.mkdir(parents=True,exist_ok=True)
            for key,name in ASSETS.items():
                destination=originals/name
                if not destination.exists():shutil.copyfile(objects[key],destination);destination.chmod(0o444)
            save_json(location/'SOURCE_PACKET.json',data)
        save_json(state/'FLOW.json',flow);save_json(state/'worker-command.json',command)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=B);p.add_argument('--apply',action='store_true');p.add_argument('--owner');p.add_argument('--generation',type=int)
    a=p.parse_args();flow,command,packets,summary=plan(a.root)
    if a.apply:
        if not a.owner or a.generation is None:p.error('--apply requires explicit --owner/--generation')
        apply(a.root,flow,command,packets,a.owner,a.generation)
    print(json.dumps(dict(summary,applied=a.apply),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
