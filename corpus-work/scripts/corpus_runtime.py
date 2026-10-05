"""Durable bounded corpus jobs; classify material outcomes before admission; retain exact continuation stages."""
import argparse, contextlib, datetime, fcntl, json, os, re, sqlite3, subprocess, sys, time
from pathlib import Path
from corpus_control_protocol import controller_guard, require_owner, load_json, save_json, normalize_key, validate_result

def owned_write(fn):
    def guarded(self,*args,**kwargs):
        with controller_guard(self.db.parent,self.controller_id,self.generation): return fn(self,*args,**kwargs)
    return guarded

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def identity(pid):
    try:
        p=Path('/proc')/str(pid); s=(p/'stat').read_text().rsplit(')',1)[1].split()
        return None if s[0]=='Z' else {'pid':int(pid),'start_time':s[19],'cwd':os.readlink(p/'cwd')}
    except (OSError,ValueError): return None
def live(row):
    x=identity(row.get('pid'))
    return bool(x and x['start_time']==row.get('proc_start') and x['cwd']==row.get('proc_cwd'))
class Runtime:
    def __init__(self,db,controller_id=None,generation=None,readonly=False):
        self.controller_id=controller_id; self.generation=generation; self.readonly=readonly
        self.db=Path(db).absolute()
        if readonly: return
        self.assert_owner()
        self.db.parent.mkdir(parents=True,exist_ok=True)
        with controller_guard(self.db.parent,self.controller_id,self.generation), contextlib.closing(self.connect()) as c:
            c.executescript("""CREATE TABLE IF NOT EXISTS jobs(job_id TEXT PRIMARY KEY,workspace TEXT NOT NULL,stages TEXT NOT NULL,state TEXT NOT NULL,next_stage INTEGER DEFAULT 0,pid INTEGER,proc_start TEXT,proc_cwd TEXT,exit_record TEXT,created_at TEXT,updated_at TEXT,exit_code INTEGER,detail TEXT);
            CREATE TABLE IF NOT EXISTS handoff_refs(handoff_path TEXT PRIMARY KEY,record TEXT NOT NULL,imported_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS claims(work_key TEXT PRIMARY KEY,job_id TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS stage_runs(job_id TEXT,stage_index INTEGER,state TEXT,started_at TEXT,ended_at TEXT,exit_code INTEGER,stdout TEXT,stderr TEXT,PRIMARY KEY(job_id,stage_index));""")
            cols={r[1] for r in c.execute('PRAGMA table_info(jobs)')}
            for column,kind in [('next_attempt_at','REAL DEFAULT 0'),('retry_count','INTEGER DEFAULT 0'),('child_pid','INTEGER'),('child_start','TEXT'),('child_cwd','TEXT'),('job_spec','TEXT'),('result_status','TEXT'),('reason_code','TEXT'),('block_accounted','INTEGER DEFAULT 0')]:
                if column not in cols: c.execute('ALTER TABLE jobs ADD COLUMN '+column+' '+kind)
            c.execute('CREATE TABLE IF NOT EXISTS stage_history AS SELECT * FROM stage_runs WHERE 0')
            c.commit()
    def assert_owner(self): require_owner(self.db.parent,self.controller_id,self.generation)
    @owned_write
    def finish(self,job_id,code):
        row=self.status(job_id)[0];spec=row.get('job_spec');state='needs_recovery';reason='result_missing';status=None;detail='JOB_RESULT required; exit code is not material completion'
        if spec and Path(spec['result_path']).is_file():
            try:
                flow=load_json(self.db.parent/'FLOW.json');units={u['problem_id']:u for b in flow['blocks'] if b['block_id']==spec['block_id'] for u in b['units']}
                status=validate_result(load_json(spec['result_path']),spec,units);state='collected';reason=None;detail='valid '+status+' result; root admission remains separate'
            except (ValueError,KeyError,OSError,TypeError) as e:reason='result_invalid';detail=str(e)
        with self.tx() as c:c.execute('UPDATE jobs SET state=?,exit_code=?,result_status=?,reason_code=?,detail=?,updated_at=? WHERE job_id=?',(state,code,status,reason,detail,now(),job_id))
    @owned_write
    def register(self,spec):
        if spec.get('schema_version')!=2 or spec.get('record_type')!='job_spec':raise ValueError('v2 job_spec required')
        required={'schema_version','record_type','job_id','attempt_id','block_id','actor','unit_ids','work_keys','workspace','stages','result_path'}
        if not required<=set(spec) or set(spec)-required-{'previous_job_id','resume_unit_ids'}:raise ValueError('exact immutable job fields required')
        for key in ('job_id','attempt_id','block_id'):
            if not isinstance(spec.get(key),str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}',spec[key]):raise ValueError('invalid '+key)
        if not isinstance(spec['stages'],list) or not spec['stages']:raise ValueError('stages required')
        for stage in spec['stages']:
            if not stage.get('name') or not isinstance(stage.get('argv'),list) or not stage['argv'] or not all(isinstance(v,str) and v for v in stage['argv']) or set(stage)-{'name','argv','stdin','stdout','stderr','retry_on_limit'}:raise ValueError('stage structure invalid')
        ids=spec['unit_ids'];keys=sorted(set(normalize_key(k) for k in spec['work_keys']))
        if not ids or len(set(ids))!=len(ids) or any(not isinstance(i,str) or not i.isdecimal() for i in ids):raise ValueError('exact string unit IDs required')
        if any('id:'+i not in keys for i in ids):raise ValueError('explicit unit id claims required')
        flow=self.flow();blocks={b['block_id']:b for b in flow['blocks']};block=blocks.get(spec['block_id'])
        if not block or not set(ids)<=set(u['problem_id'] for u in block['units']):raise ValueError('job scope outside FLOW block')
        required={'id:'+i for i in ids}|{normalize_key(u['work_key']) for u in block['units'] if u['problem_id'] in ids}
        if set(keys)!=required:raise ValueError('job exact work key set mismatch')
        spec=dict(spec,work_keys=keys);encoded=json.dumps(spec,sort_keys=True)
        previous=spec.get('previous_job_id')
        with self.tx() as c:
            old=c.execute('SELECT * FROM jobs WHERE job_id=?',(spec['job_id'],)).fetchone()
            if old:
                if old['job_spec']!=encoded:raise ValueError('immutable job/attempt input mismatch')
                return self.status(spec['job_id'])
            if spec.get('actor')!={'owner':self.controller_id,'generation':self.generation}:raise ValueError('new job actor mismatch')
            if c.execute("SELECT 1 FROM jobs WHERE json_extract(job_spec,'$.block_id')=? AND json_extract(job_spec,'$.attempt_id')=?",(spec['block_id'],spec['attempt_id'])).fetchone():raise ValueError('attempt identity already registered')
            if previous:
                prior=c.execute('SELECT * FROM jobs WHERE job_id=?',(previous,)).fetchone()
                if not prior or prior['state'] not in ('collected','needs_recovery','failed','rate_limited','quota_wait'):raise ValueError('confirmed terminal predecessor required')
                if live(dict(prior)) or live({'pid':prior['child_pid'],'proc_start':prior['child_start'],'proc_cwd':prior['child_cwd']}):raise ValueError('predecessor/child still live')
                prior_spec=json.loads(prior['job_spec']) if prior['job_spec'] else None
                if not prior_spec or prior_spec['block_id']!=spec['block_id']:raise ValueError('predecessor block differs')
                if prior['result_status']=='partial':
                    unfinished={u['problem_id'] for u in load_json(prior_spec['result_path'])['units'] if u['disposition']=='unfinished'}
                    if set(ids)!=unfinished:raise ValueError('continuation must only inherit unfinished scope')
                for key in keys:
                    held=c.execute('SELECT job_id FROM claims WHERE work_key=?',(key,)).fetchone()
                    if held and held[0]!=previous:raise ValueError('work claimed by another attempt')
            workspace=str(Path(spec['workspace']).resolve(strict=True));stages=json.dumps(spec['stages'],sort_keys=True)
            c.execute('INSERT INTO jobs(job_id,workspace,stages,state,created_at,updated_at,job_spec) VALUES(?,?,?,?,?,?,?)',(spec['job_id'],workspace,stages,'claimed',now(),now(),encoded))
            for key in keys:
                c.execute('INSERT INTO claims(work_key,job_id) VALUES(?,?) ON CONFLICT(work_key) DO UPDATE SET job_id=excluded.job_id WHERE claims.job_id=?',(key,spec['job_id'],previous))
                if c.execute('SELECT job_id FROM claims WHERE work_key=?',(key,)).fetchone()[0]!=spec['job_id']:raise ValueError('work already claimed')
        return self.status(spec['job_id'])
    @owned_write
    def import_reference(self,handoff):
        path=str(Path(handoff).resolve(strict=True));record=load_json(path);encoded=json.dumps(record,sort_keys=True)
        if not record.get('candidate_root') or not isinstance(record.get('items',record.get('units')),list):raise ValueError('handoff units/reference required')
        with self.tx() as c:
            old=c.execute('SELECT record FROM handoff_refs WHERE handoff_path=?',(path,)).fetchone()
            if old and old[0]!=encoded:raise ValueError('handoff historical reference changed')
            c.execute('INSERT OR IGNORE INTO handoff_refs VALUES(?,?,?)',(path,encoded,now()))
        return {'status':'reference_imported','handoff':path,'count_increment':0,'admission_increment':0}
    def flow(self):
        flow=load_json(self.db.parent/'FLOW.json');blocks=flow['blocks'];mapping={b['block_id']:b for b in blocks}
        if flow.get('schema_version')!=2 or flow.get('record_type')!='flow' or len(mapping)!=len(blocks):raise ValueError('invalid FLOW identity')
        ids=set();works={}
        for b in blocks:
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}',b['block_id']):raise ValueError('invalid block identity')
            for u in b['units']:
                pid=u['problem_id'];key=normalize_key(u['work_key'])
                if not isinstance(pid,str) or not pid.isdecimal() or pid in ids:raise ValueError('FLOW duplicate/invalid unit ID')
                ids.add(pid)
                if key in works and works[key]!=b['block_id']:raise ValueError('FLOW work spans concurrent blocks')
                works[key]=b['block_id']
            seen=set();cur=b['block_id']
            while cur is not None:
                if cur in seen or cur not in mapping:raise ValueError('FLOW cycle/missing successor')
                seen.add(cur);cur=mapping[cur]['next_block_id']
        return flow
    @owned_write
    def schedule(self,review_backlog=0):
        flow=self.flow();rows=self.status();cfg_path=self.db.parent/'worker-command.json'
        if not cfg_path.is_file():return []
        cfg=load_json(cfg_path);blocks={b['block_id']:b for b in flow['blocks']};created=[]
        for block in flow['blocks']:
            if not block['enabled']:continue
            runs=[r for r in rows if r.get('job_spec') and r['job_spec']['block_id']==block['block_id']]
            prior=runs[-1] if runs else None
            checkpoint=None
            if prior:
                if prior['live'] or prior['child_live'] or prior['state'] not in ('collected','rate_limited','needs_recovery'):continue
                if prior['state']=='needs_recovery':continue
                if prior['state']=='rate_limited' and prior['next_attempt_at']>time.time():continue
                if prior['state']=='collected':
                    checkpoint=load_json(prior['job_spec']['result_path'])
                    recent=runs[-3:]
                    if len(recent)==3 and all(r['state']=='collected' and r.get('result_status')=='partial' for r in recent):
                        signatures=[]
                        for finished in recent:
                            saved=load_json(finished['job_spec']['result_path'])
                            signatures.append((tuple(sorted(finished['job_spec']['unit_ids'])),tuple(sorted((u['problem_id'],u['last_completed_stage'],u['next_stage'],u['disposition']) for u in saved['units']))))
                        if signatures[0]==signatures[1]==signatures[2]:
                            detail='unchanged checkpoint across 3 consecutive partial attempts; controller must inspect preserved work before explicit continuation'
                            if prior.get('reason_code')!='tool_failure' or prior.get('detail')!=detail:
                                with self.tx() as c:c.execute("UPDATE jobs SET reason_code='tool_failure',detail=?,updated_at=? WHERE job_id=?",(detail,now(),prior['job_id']))
                            continue
                    ids=[u['problem_id'] for u in checkpoint['units'] if u['disposition']=='unfinished']
                    if not ids:
                        with self.tx() as c:c.execute('UPDATE jobs SET block_accounted=1 WHERE job_id=?',(prior['job_id'],))
                        continue
                else:ids=prior['job_spec']['unit_ids']
            else:
                if review_backlog>=25:continue
                predecessors=[b for b in flow['blocks'] if b['next_block_id']==block['block_id']]
                if predecessors and not all(any(r.get('job_spec') and r['job_spec']['block_id']==b['block_id'] and r['block_accounted'] for r in rows) for b in predecessors):continue
                ids=[u['problem_id'] for u in block['units']]
            number=len(runs)+1;job_id=block['block_id']+'-a'+str(number).zfill(3);attempt='a'+str(number).zfill(3)
            folder=self.db.parent/'jobs'/job_id;folder.mkdir(parents=True,exist_ok=True);result=folder/'JOB_RESULT.json';specpath=folder/'JOB_SPEC.json'
            units=[u for u in block['units'] if u['problem_id'] in ids];workspace=cfg.get('workspace') or os.path.commonpath([u['workspace'] for u in units])
            replacements={'job_spec':str(specpath),'result_path':str(result),'workspace':workspace,'job_id':job_id,'attempt_id':attempt}
            argv=[]
            for value in cfg['argv']:
                for key,replacement in replacements.items():value=value.replace('{'+key+'}',replacement)
                argv.append(value)
            stage={'name':'source-block-worker','argv':argv,'stdout':str(folder/'events.private.jsonl'),'stderr':str(folder/'stderr.private.txt'),'retry_on_limit':True}
            if cfg.get('task_file'):
                task=folder/'TASK.md';task.write_text(Path(cfg['task_file']).read_text()+'\n\nAUTHORITATIVE JOB INPUT\n'+json.dumps({'job_id':job_id,'attempt_id':attempt,'block_id':block['block_id'],'units':units,'result_path':str(result),'previous_result':checkpoint},indent=2),encoding='utf-8');stage['stdin']=str(task)
            spec={'schema_version':2,'record_type':'job_spec','job_id':job_id,'attempt_id':attempt,'block_id':block['block_id'],'actor':{'owner':self.controller_id,'generation':self.generation},'unit_ids':ids,'work_keys':sorted({'id:'+i for i in ids}|{normalize_key(u['work_key']) for u in units}),'workspace':workspace,'stages':[stage],'result_path':str(result)}
            if prior:spec.update(previous_job_id=prior['job_id'],resume_unit_ids=ids)
            if specpath.exists() and load_json(specpath)!=spec:raise ValueError('persisted deterministic attempt differs')
            save_json(specpath,spec);self.register(spec)
            if prior and prior['state']=='rate_limited':
                with self.tx() as c:c.execute('UPDATE jobs SET retry_count=? WHERE job_id=?',(prior['retry_count'],job_id))
            created.append(job_id)
        return created
    def connect(self):
        c=sqlite3.connect('file:'+str(self.db)+'?mode=ro',uri=True,timeout=30) if self.readonly else sqlite3.connect(self.db,timeout=30); c.row_factory=sqlite3.Row; return c
    @contextlib.contextmanager
    def tx(self):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE'); yield c; c.commit()
        except BaseException: c.rollback(); raise
        finally: c.close()
    @owned_write
    def claim(self,job_id,work_key,workspace,stages):
        raise ValueError('v2 immutable job_spec required; use register')
    @owned_write
    def revise(self,job_id,previous_job,workspace,stages,additional_keys=()):
        raise ValueError('v2 previous_job_id and exact unit scope required; use register')
    def status(self,job_id=None):
        if not self.db.exists(): return []
        with contextlib.closing(self.connect()) as c:
            rows=c.execute('SELECT * FROM jobs'+(' WHERE job_id=?' if job_id else '')+' ORDER BY created_at',(job_id,) if job_id else ()).fetchall()
            out=[]
            for r in rows:
                r=dict(r); r['live']=live(r); r['stages']=json.loads(r['stages']); r['job_spec']=json.loads(r['job_spec']) if r.get('job_spec') else None
                r['child_live']=live({'pid':r['child_pid'],'proc_start':r['child_start'],'proc_cwd':r['child_cwd']})
                r['work_keys']=[x[0] for x in c.execute('SELECT work_key FROM claims WHERE job_id=? ORDER BY work_key',(r['job_id'],))]
                r['stage_runs']=[dict(x) for x in c.execute('SELECT * FROM stage_runs WHERE job_id=? ORDER BY stage_index',(r['job_id'],))]
                out.append(r)
            return out
    def lock_path(self,job_id): return self.db.parent/(job_id+'.lock')
    @owned_write
    def adopt(self,job_id,pid,proc_start=None,exit_record=None):
        rows=self.status(job_id)
        if not rows or not rows[0].get('job_spec'):raise ValueError('register immutable v2 input before adopt')
        row=rows[0];x=identity(pid)
        if not x:
            if not exit_record or not Path(exit_record).is_file():raise ValueError('terminal record required for dead process')
            terminal=load_json(exit_record);code=terminal.get('exit_code')
            if not isinstance(code,int):raise ValueError('terminal exit code missing')
            self.finish(job_id,code);return self.status(job_id)
        args=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
        if (proc_start is not None and x['start_time']!=str(proc_start)) or not (x['cwd']==row['workspace'] or os.fsencode(row['workspace']) in args):raise ValueError('existing process identity mismatch')
        with self.tx() as c:
            if row['state']=='claimed':c.execute("UPDATE jobs SET state='running',pid=?,proc_start=?,proc_cwd=?,exit_record=?,updated_at=? WHERE job_id=?",(pid,x['start_time'],x['cwd'],exit_record,now(),job_id))
            elif (row['pid'],row['proc_start'],row['proc_cwd'])!=(pid,x['start_time'],x['cwd']):raise ValueError('adopt identity differs')
        return self.status(job_id)
    @owned_write
    def collect(self,job_id=None):
        self.assert_owner()
        self._children=[p for p in self.__dict__.get('_children',[]) if p.poll() is None]
        for row in self.status(job_id):
            if row['state'] in ('awaiting_admission','needs_recovery') and not row['live'] and not row['child_live'] and (row['state']=='awaiting_admission' or (row.get('job_spec') and Path(row['job_spec']['result_path']).is_file())):
                self.finish(row['job_id'],row['exit_code'] or 0)
                continue
            if row['state'] not in ('running','starting','orphan_running'): continue
            if row['exit_record']:
                p=Path(row['exit_record'])
                if p.exists() and not row['live']:
                    terminal=json.loads(p.read_text()); code=terminal.get('exit_code',terminal.get('returncode',terminal.get('rc')))
                    if not isinstance(code,int): continue
                    self.finish(row['job_id'],code)
                    continue
                if row['live']: continue
                with self.tx() as c: c.execute("UPDATE jobs SET state='needs_recovery',detail='dead adopted PID without terminal',updated_at=? WHERE job_id=?",(now(),row['job_id']))
                continue
            with self.lock_path(row['job_id']).open('a') as lock:
                try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError: continue
                with self.tx() as c:
                    current=dict(c.execute('SELECT * FROM jobs WHERE job_id=?',(row['job_id'],)).fetchone())
                    if current['state']=='starting' and (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(current['updated_at'])).total_seconds()<30: continue
                    if current['state'] in ('running','starting','orphan_running') and not live(current):
                        receipt=Path(current['workspace'])/'.corpus-runtime'/row['job_id']/f"{current['next_stage']:03}.result.json"
                        if receipt.is_file() and current.get('job_spec'):
                            rr=load_json(receipt);spec=json.loads(current['job_spec'])
                            if rr.get('job_id')==row['job_id'] and rr.get('attempt_id')==spec['attempt_id'] and rr.get('stage_index')==current['next_stage'] and isinstance(rr.get('exit_code'),int):
                                if rr['exit_code']==0:
                                    c.execute("UPDATE jobs SET next_stage=next_stage+1,state='queued',exit_code=0,updated_at=? WHERE job_id=?",(now(),row['job_id']))
                                else:c.execute("UPDATE jobs SET state='needs_recovery',reason_code='tool_failure',exit_code=?,updated_at=? WHERE job_id=?",(rr['exit_code'],now(),row['job_id']))
                                continue

                        stage=c.execute('SELECT state FROM stage_runs WHERE job_id=? AND stage_index=?',(row['job_id'],current['next_stage'])).fetchone()
                        child_active=live({'pid':current['child_pid'],'proc_start':current['child_start'],'proc_cwd':current['child_cwd']})
                        if child_active:
                            state='orphan_running';detail='runner dead but stage child remains live; no replay or claim transfer'
                        elif stage and stage['state']=='running':
                            state='needs_recovery'; detail='stage outcome unknown; review before replay'
                        else:
                            state='queued'; detail='runner ended between stages; resume next stage'
                        c.execute('UPDATE jobs SET state=?,detail=?,updated_at=? WHERE job_id=?',(state,detail,now(),row['job_id']))
        return self.status(job_id)
    @owned_write
    def start(self,job_id,max_jobs=3):
        self.assert_owner()
        with self.tx() as c:
            row=c.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
            if not row: raise KeyError(job_id)
            if not row['job_spec']:raise ValueError('legacy job needs explicit v2 recovery input')
            if row['state'] in ('failed','interrupted','orphan_running'): raise ValueError('failed/unknown stage requires reviewed revision; no automatic replay')
            if row['state'] in ('running','starting','collected','needs_recovery','quota_wait','rate_limited'): return self.status(job_id)
            cooling=c.execute("SELECT COALESCE(MAX(next_attempt_at),0) FROM jobs WHERE state='rate_limited'").fetchone()[0]
            if cooling>time.time(): return self.status(job_id)
            c.execute("UPDATE jobs SET state='queued',updated_at=? WHERE job_id=?",(now(),job_id))
            active=c.execute("SELECT COUNT(*) FROM jobs WHERE state IN ('running','starting')").fetchone()[0]
            for other in c.execute("SELECT * FROM jobs WHERE state IN ('interrupted','orphan_running')"):
                if live({'pid':other['child_pid'],'proc_start':other['child_start'],'proc_cwd':other['child_cwd']}): active+=1
            if active>=max_jobs: return self.status(job_id)
            c.execute("UPDATE jobs SET state='starting',updated_at=? WHERE job_id=?",(now(),job_id))
        with (self.db.parent/(job_id+'.runner.log')).open('ab') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--db',str(self.db),*(['--controller-id',self.controller_id,'--generation',str(self.generation)] if self.controller_id else []),'_runner','--job-id',job_id],cwd=row['workspace'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
            self.__dict__.setdefault('_children',[]).append(child)
            x=identity(child.pid)
            if x:
                with self.tx() as c: c.execute("UPDATE jobs SET pid=?,proc_start=?,proc_cwd=? WHERE job_id=? AND state='starting'",(x['pid'],x['start_time'],x['cwd'],job_id))
        return self.status(job_id)
    def resume(self,job_id): self.collect(job_id); return self.start(job_id)
    def run_job(self,job_id):
        with self.lock_path(job_id).open('a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return
            with controller_guard(self.db.parent,self.controller_id,self.generation),self.tx() as c:
                row=c.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
                if row['state']!='starting':return
                x=identity(os.getpid());c.execute("UPDATE jobs SET state='running',pid=?,proc_start=?,proc_cwd=?,updated_at=? WHERE job_id=?",(x['pid'],x['start_time'],x['cwd'],now(),job_id))
            stages=json.loads(row['stages']);spec=json.loads(row['job_spec'])
            for n in range(row['next_stage'],len(stages)):
                output=Path(row['workspace'])/'.corpus-runtime'/job_id;output.mkdir(parents=True,exist_ok=True)
                out=Path(stages[n].get('stdout',output/f'{n:03}.stdout'));err=Path(stages[n].get('stderr',output/f'{n:03}.stderr'))
                receipt=output/f'{n:03}.result.json'
                with controller_guard(self.db.parent,self.controller_id,self.generation),self.tx() as c:
                    c.execute('INSERT INTO stage_runs VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(job_id,stage_index) DO UPDATE SET state=excluded.state,started_at=excluded.started_at,ended_at=NULL,exit_code=NULL,stdout=excluded.stdout,stderr=excluded.stderr',(job_id,n,'running',now(),None,None,str(out),str(err)))
                    try:
                        a=out.open('ab');b=err.open('ab');inp=Path(stages[n]['stdin']).open('rb') if stages[n].get('stdin') else subprocess.DEVNULL
                        child=subprocess.Popen(stages[n]['argv'],cwd=row['workspace'],stdin=inp,stdout=a,stderr=b)
                        x=identity(child.pid)
                        if x:c.execute('UPDATE jobs SET child_pid=?,child_start=?,child_cwd=? WHERE job_id=?',(x['pid'],x['start_time'],x['cwd'],job_id))
                    except OSError as error:
                        code=127;err.write_text(str(error))
                        child=None
                if child:
                    try:code=child.wait()
                    finally:
                        a.close();b.close()
                        if inp!=subprocess.DEVNULL:inp.close()
                # Private attempt outcome survives owner handoff; only current actor updates shared runtime.
                save_json(receipt,{'job_id':job_id,'attempt_id':spec['attempt_id'],'stage_index':n,'exit_code':code,'ended_at':now()})
                try:
                    with controller_guard(self.db.parent,self.controller_id,self.generation),self.tx() as c:
                        c.execute('UPDATE stage_runs SET state=?,ended_at=?,exit_code=? WHERE job_id=? AND stage_index=?',('succeeded' if code==0 else 'failed',now(),code,job_id,n))
                        if code:
                            text=out.read_text(errors='replace')+err.read_text(errors='replace')
                            refused=stages[n].get('retry_on_limit') is True and 'Concurrency limit exceeded' in text and 'command_execution' not in text and 'item.started' not in text
                            count=row['retry_count']
                            state='rate_limited' if refused and count<3 else ('quota_wait' if refused else 'needs_recovery')
                            delay=60*(2**min(count,2)) if refused else 0
                            c.execute('UPDATE jobs SET state=?,exit_code=?,next_attempt_at=?,retry_count=retry_count+1,reason_code=?,detail=?,updated_at=? WHERE job_id=?',(state,code,time.time()+delay,'model_quota' if refused else 'tool_failure','confirmed pre-command refusal; new immutable attempt required' if refused else 'inspect stage outcome; no blind replay',now(),job_id))
                        else:c.execute('UPDATE jobs SET next_stage=?,exit_code=0,updated_at=? WHERE job_id=?',(n+1,now(),job_id))
                except ValueError:return
                if code:return
            self.finish(job_id,0)
    def serve(self,poll_seconds=2,max_jobs=3):
        if max_jobs<1 or max_jobs>8: raise ValueError('max_jobs must be1..8')
        while True:
            rows=self.collect(); capacity=max_jobs-sum(r['state'] in ('running','starting') or r['child_live'] for r in rows)
            for r in rows:
                if capacity<=0: break
                if r['state'] in ('claimed','queued') and r['next_attempt_at']<=time.time(): self.start(r['job_id'],max_jobs); capacity-=1
            time.sleep(poll_seconds)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);p.add_argument('--controller-id');p.add_argument('--generation',type=int);sub=p.add_subparsers(dest='command',required=True)
    for name in ('claim','revise'):
        c=sub.add_parser(name);c.add_argument('--spec',required=True)
    for name in ('run','resume','_runner'):
        c=sub.add_parser(name);c.add_argument('--job-id',required=True)
    for name in ('status','collect'):
        c=sub.add_parser(name);c.add_argument('--job-id')
    c=sub.add_parser('import-handoff');c.add_argument('--handoff',required=True)
    c=sub.add_parser('serve');c.add_argument('--max-jobs',type=int,default=3);c.add_argument('--poll-seconds',type=float,default=2)
    c=sub.add_parser('adopt');c.add_argument('--spec',required=True);c.add_argument('--pid',type=int,required=True);c.add_argument('--proc-start');c.add_argument('--exit-record')
    a=p.parse_args();r=Runtime(a.db,a.controller_id,a.generation,readonly=a.command=='status')
    if a.command=='import-handoff':value=r.import_reference(a.handoff)
    elif a.command in ('claim','revise'):value=r.register(load_json(a.spec))
    elif a.command=='adopt':
        spec=load_json(a.spec);r.register(spec);value=r.adopt(spec['job_id'],a.pid,a.proc_start,a.exit_record)
    elif a.command=='_runner':r.run_job(a.job_id);return
    elif a.command=='serve':r.serve(a.poll_seconds,a.max_jobs);return
    else:value=getattr(r,'start' if a.command=='run' else a.command)(a.job_id)
    print(json.dumps(value,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
