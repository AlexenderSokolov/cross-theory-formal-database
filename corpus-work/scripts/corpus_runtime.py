"""Durable bounded corpus jobs; completion is only awaiting_admission."""
import argparse, contextlib, datetime, fcntl, json, os, re, sqlite3, subprocess, sys, time
from pathlib import Path

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
    def __init__(self,db):
        self.db=Path(db).absolute(); self.db.parent.mkdir(parents=True,exist_ok=True)
        with contextlib.closing(self.connect()) as c:
            c.executescript("""CREATE TABLE IF NOT EXISTS jobs(job_id TEXT PRIMARY KEY,workspace TEXT NOT NULL,stages TEXT NOT NULL,state TEXT NOT NULL,next_stage INTEGER DEFAULT 0,pid INTEGER,proc_start TEXT,proc_cwd TEXT,exit_record TEXT,created_at TEXT,updated_at TEXT,exit_code INTEGER,detail TEXT);
            CREATE TABLE IF NOT EXISTS claims(work_key TEXT PRIMARY KEY,job_id TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS stage_runs(job_id TEXT,stage_index INTEGER,state TEXT,started_at TEXT,ended_at TEXT,exit_code INTEGER,stdout TEXT,stderr TEXT,PRIMARY KEY(job_id,stage_index));""")
            cols={r[1] for r in c.execute('PRAGMA table_info(jobs)')}
            for column,kind in [('next_attempt_at','REAL DEFAULT 0'),('retry_count','INTEGER DEFAULT 0'),('child_pid','INTEGER'),('child_start','TEXT'),('child_cwd','TEXT')]:
                if column not in cols: c.execute('ALTER TABLE jobs ADD COLUMN '+column+' '+kind)
            c.execute('CREATE TABLE IF NOT EXISTS stage_history AS SELECT * FROM stage_runs WHERE 0')
            c.commit()
    def connect(self):
        c=sqlite3.connect(self.db,timeout=30); c.row_factory=sqlite3.Row; return c
    @contextlib.contextmanager
    def tx(self):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE'); yield c; c.commit()
        except BaseException: c.rollback(); raise
        finally: c.close()
    def claim(self,job_id,work_key,workspace,stages):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}',job_id): raise ValueError('invalid JOB_ID')
        workspace=str(Path(workspace).resolve(strict=True))
        if not Path(workspace).is_dir() or not stages: raise ValueError('workspace/stages required')
        for s in stages:
            if not s.get('name') or not isinstance(s.get('argv'),list) or not s['argv'] or not all(isinstance(v,str) for v in s['argv']): raise ValueError('name and argv list required')
        keys=sorted(set(work_key if isinstance(work_key,list) else [work_key]))
        if not keys or not all(isinstance(k,str) and k for k in keys): raise ValueError('work keys required')
        encoded=json.dumps(stages,sort_keys=True)
        with self.tx() as c:
            old=c.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
            if old:
                prior=[r[0] for r in c.execute('SELECT work_key FROM claims WHERE job_id=? ORDER BY work_key',(job_id,))]
                if (old['workspace'],old['stages'],prior)!=(workspace,encoded,keys): raise ValueError('JOB_ID input mismatch')
            else:
                c.execute('INSERT INTO jobs(job_id,workspace,stages,state,created_at,updated_at) VALUES(?,?,?,?,?,?)',(job_id,workspace,encoded,'claimed',now(),now()))
                for key in keys: c.execute('INSERT INTO claims VALUES(?,?)',(key,job_id))
        return self.status(job_id)
    def revise(self,job_id,previous_job,workspace,stages,additional_keys=()):
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}',job_id): raise ValueError('invalid JOB_ID')
        workspace=str(Path(workspace).resolve(strict=True));encoded=json.dumps(stages,sort_keys=True)
        with self.tx() as c:
            old=c.execute('SELECT * FROM jobs WHERE job_id=?',(previous_job,)).fetchone()
            if not old or old['state'] not in ('failed','interrupted'): raise ValueError('reviewed stopped predecessor required')
            if live(dict(old)) or live({'pid':old['child_pid'],'proc_start':old['child_start'],'proc_cwd':old['child_cwd']}): raise ValueError('predecessor process still live; cannot transfer claims')
            prior=c.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
            if prior:
                if (prior['workspace'],prior['stages'])!=(workspace,encoded): raise ValueError('revision JOB_ID mismatch')
                return self.status(job_id)
            c.execute('INSERT INTO jobs(job_id,workspace,stages,state,created_at,updated_at,detail) VALUES(?,?,?,?,?,?,?)',(job_id,workspace,encoded,'claimed',now(),now(),'reviewed revision of '+previous_job))
            c.execute('UPDATE claims SET job_id=? WHERE job_id=?',(job_id,previous_job))
            for key in additional_keys: c.execute('INSERT INTO claims VALUES(?,?)',(key,job_id))
        return self.status(job_id)
    def status(self,job_id=None):
        with contextlib.closing(self.connect()) as c:
            rows=c.execute('SELECT * FROM jobs'+(' WHERE job_id=?' if job_id else '')+' ORDER BY created_at',(job_id,) if job_id else ()).fetchall()
            out=[]
            for r in rows:
                r=dict(r); r['live']=live(r); r['stages']=json.loads(r['stages'])
                r['child_live']=live({'pid':r['child_pid'],'proc_start':r['child_start'],'proc_cwd':r['child_cwd']})
                r['work_keys']=[x[0] for x in c.execute('SELECT work_key FROM claims WHERE job_id=? ORDER BY work_key',(r['job_id'],))]
                r['stage_runs']=[dict(x) for x in c.execute('SELECT * FROM stage_runs WHERE job_id=? ORDER BY stage_index',(r['job_id'],))]
                out.append(r)
            return out
    def lock_path(self,job_id): return self.db.parent/(job_id+'.lock')
    def adopt(self,job_id,work_key,workspace,pid,proc_start=None,exit_record=None):
        x=identity(pid)
        if x is None and exit_record and Path(exit_record).is_file():
            terminal=json.loads(Path(exit_record).read_text())
            code=terminal.get('exit_code')
            if not isinstance(code,int): raise ValueError('terminal exit_code missing')
            self.claim(job_id,work_key,workspace,[{'name':'existing-worker','argv':['existing-process']}])
            with self.tx() as c:
                c.execute("UPDATE jobs SET state=?,pid=?,exit_record=?,exit_code=?,detail='imported terminal; root review pending',updated_at=? WHERE job_id=? AND state='claimed'",('awaiting_admission' if code==0 else 'failed',pid,str(Path(exit_record).absolute()),code,now(),job_id))
            return self.status(job_id)
        owned=False
        if x:
            args=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
            workspace_path=str(Path(workspace).resolve())
            owned=(x['cwd']==workspace_path or os.fsencode(workspace_path+'/run.py') in args or os.fsencode(workspace_path) in args)
        if not x or not owned or (proc_start is not None and x['start_time']!=str(proc_start)): raise ValueError('existing process identity mismatch')
        self.claim(job_id,work_key,workspace,[{'name':'existing-worker','argv':['existing-process']}])
        with self.tx() as c:
            old=c.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
            if old['state']=='claimed':
                c.execute("UPDATE jobs SET state='running',pid=?,proc_start=?,proc_cwd=?,exit_record=?,updated_at=? WHERE job_id=?",(pid,x['start_time'],x['cwd'],str(Path(exit_record).absolute()) if exit_record else None,now(),job_id))
            elif (old['pid'],old['proc_start'],old['proc_cwd'])!=(pid,x['start_time'],x['cwd']): raise ValueError('adopt identity differs')
        return self.status(job_id)
    def collect(self,job_id=None):
        self._children=[p for p in self.__dict__.get('_children',[]) if p.poll() is None]
        for row in self.status(job_id):
            if row['state'] not in ('running','starting','orphan_running'): continue
            if row['exit_record']:
                p=Path(row['exit_record'])
                if p.exists() and not row['live']:
                    terminal=json.loads(p.read_text()); code=terminal.get('exit_code',terminal.get('returncode',terminal.get('rc')))
                    if not isinstance(code,int): continue
                    with self.tx() as c:
                        c.execute('UPDATE jobs SET state=?,exit_code=?,detail=?,updated_at=? WHERE job_id=? AND state=?',('awaiting_admission' if code==0 else 'failed',code,'existing process terminal; admission pending' if code==0 else 'existing process failed',now(),row['job_id'],'running'))
                    continue
                if row['live']: continue
                with self.tx() as c: c.execute("UPDATE jobs SET state='interrupted',detail='dead adopted PID without terminal',updated_at=? WHERE job_id=?",(now(),row['job_id']))
                continue
            with self.lock_path(row['job_id']).open('a') as lock:
                try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError: continue
                with self.tx() as c:
                    current=dict(c.execute('SELECT * FROM jobs WHERE job_id=?',(row['job_id'],)).fetchone())
                    if current['state']=='starting' and (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(current['updated_at'])).total_seconds()<30: continue
                    if current['state'] in ('running','starting','orphan_running') and not live(current):
                        stage=c.execute('SELECT state FROM stage_runs WHERE job_id=? AND stage_index=?',(row['job_id'],current['next_stage'])).fetchone()
                        child_active=live({'pid':current['child_pid'],'proc_start':current['child_start'],'proc_cwd':current['child_cwd']})
                        if child_active:
                            state='orphan_running';detail='runner dead but stage child remains live; no replay or claim transfer'
                        elif stage and stage['state']=='running':
                            state='interrupted'; detail='stage outcome unknown; review before replay'
                        else:
                            state='queued'; detail='runner ended between stages; resume next stage'
                        c.execute('UPDATE jobs SET state=?,detail=?,updated_at=? WHERE job_id=?',(state,detail,now(),row['job_id']))
        return self.status(job_id)
    def start(self,job_id):
        with self.tx() as c:
            row=c.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
            if not row: raise KeyError(job_id)
            if row['state'] in ('failed','interrupted','orphan_running'): raise ValueError('failed/unknown stage requires reviewed revision; no automatic replay')
            if row['state'] in ('running','starting','awaiting_admission'): return self.status(job_id)
            cooling=c.execute("SELECT COALESCE(MAX(next_attempt_at),0) FROM jobs WHERE state='rate_limited'").fetchone()[0]
            if cooling>time.time(): return self.status(job_id)
            c.execute("UPDATE jobs SET state='queued',updated_at=? WHERE job_id=?",(now(),job_id))
            active=c.execute("SELECT COUNT(*) FROM jobs WHERE state IN ('running','starting')").fetchone()[0]
            for other in c.execute("SELECT * FROM jobs WHERE state IN ('interrupted','orphan_running')"):
                if live({'pid':other['child_pid'],'proc_start':other['child_start'],'proc_cwd':other['child_cwd']}): active+=1
            if active>=3: return self.status(job_id)
            c.execute("UPDATE jobs SET state='starting',updated_at=? WHERE job_id=?",(now(),job_id))
        with (self.db.parent/(job_id+'.runner.log')).open('ab') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--db',str(self.db),'_runner','--job-id',job_id],cwd=row['workspace'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
            self.__dict__.setdefault('_children',[]).append(child)
            x=identity(child.pid)
            if x:
                with self.tx() as c: c.execute("UPDATE jobs SET pid=?,proc_start=?,proc_cwd=? WHERE job_id=? AND state='starting'",(x['pid'],x['start_time'],x['cwd'],job_id))
        return self.status(job_id)
    def resume(self,job_id): self.collect(job_id); return self.start(job_id)
    def run_job(self,job_id):
        with self.lock_path(job_id).open('a') as lock:
            try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError: return
            with self.tx() as c:
                row=c.execute('SELECT * FROM jobs WHERE job_id=?',(job_id,)).fetchone()
                if row['state']!='starting': return
                x=identity(os.getpid())
                c.execute("UPDATE jobs SET state='running',pid=?,proc_start=?,proc_cwd=?,updated_at=? WHERE job_id=?",(x['pid'],x['start_time'],x['cwd'],now(),job_id))
            stages=json.loads(row['stages'])
            for n in range(row['next_stage'],len(stages)):
                output=Path(row['workspace'])/'.corpus-runtime'/job_id; output.mkdir(parents=True,exist_ok=True)
                out=Path(stages[n].get('stdout',output/f'{n:03}.stdout')); err=Path(stages[n].get('stderr',output/f'{n:03}.stderr'))
                attempt=row['retry_count']
                if attempt:
                    out=output/f'{n:03}.retry{attempt}.stdout';err=output/f'{n:03}.retry{attempt}.stderr'
                with self.tx() as c:
                    c.execute('INSERT INTO stage_history SELECT * FROM stage_runs WHERE job_id=? AND stage_index=?',(job_id,n))
                    c.execute('INSERT INTO stage_runs VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(job_id,stage_index) DO UPDATE SET state=excluded.state,started_at=excluded.started_at,ended_at=NULL,exit_code=NULL,stdout=excluded.stdout,stderr=excluded.stderr',(job_id,n,'running',now(),None,None,str(out),str(err)))
                try:
                    with contextlib.ExitStack() as stack:
                        a=stack.enter_context(out.open('ab'));b=stack.enter_context(err.open('ab'))
                        inp=stack.enter_context(Path(stages[n]['stdin']).open('rb')) if stages[n].get('stdin') else subprocess.DEVNULL
                        child=subprocess.Popen(stages[n]['argv'],cwd=row['workspace'],stdin=inp,stdout=a,stderr=b,env=stages[n].get('env'))
                        child_id=identity(child.pid)
                        if child_id:
                            with self.tx() as c: c.execute('UPDATE jobs SET child_pid=?,child_start=?,child_cwd=? WHERE job_id=?',(child_id['pid'],child_id['start_time'],child_id['cwd'],job_id))
                        code=child.wait()
                except OSError as error:
                    with err.open('a') as b: b.write(str(error)+'\n')
                    code=127
                with self.tx() as c:
                    c.execute('UPDATE stage_runs SET state=?,ended_at=?,exit_code=? WHERE job_id=? AND stage_index=?',('succeeded' if code==0 else 'failed',now(),code,job_id,n))
                    if code:
                        text=out.read_text(errors='replace')+err.read_text(errors='replace')
                        safe_limit=(stages[n].get('retry_on_limit') is True and 'Concurrency limit exceeded' in text and 'command_execution' not in text and 'item.started' not in text and row['retry_count']<3)
                        if safe_limit:
                            delay=min(300,60*(2**row['retry_count']))
                            c.execute("UPDATE jobs SET state='rate_limited',exit_code=?,retry_count=retry_count+1,next_attempt_at=?,detail='explicit pre-command concurrency refusal; delayed retry',updated_at=? WHERE job_id=?",(code,time.time()+delay,now(),job_id))
                        else:
                            c.execute("UPDATE jobs SET state='failed',exit_code=?,detail='stage failed; no automatic replay',updated_at=? WHERE job_id=?",(code,now(),job_id))
                    else: c.execute('UPDATE jobs SET next_stage=?,exit_code=0,retry_count=0,next_attempt_at=0,updated_at=? WHERE job_id=?',(n+1,now(),job_id))
                terminal=stages[n].get('terminal')
                if terminal:
                    target=Path(terminal)
                    tmp=target.with_suffix(target.suffix+'.tmp')
                    tmp.write_text(json.dumps({'exit_code':code,'ended':now(),'job_id':job_id,'stage_index':n}))
                    tmp.replace(target)
                if code: return
            with self.tx() as c: c.execute("UPDATE jobs SET state='awaiting_admission',detail='technical stages finished; root admission pending',updated_at=? WHERE job_id=?",(now(),job_id))
    def serve(self,poll_seconds=2,max_jobs=3):
        if max_jobs<1 or max_jobs>3: raise ValueError('max_jobs must be1..3')
        while True:
            rows=self.collect(); capacity=max_jobs-sum(r['state'] in ('running','starting') or r['child_live'] for r in rows)
            for r in rows:
                if capacity<=0: break
                if r['state'] in ('queued','rate_limited') and r['next_attempt_at']<=time.time(): self.start(r['job_id']); capacity-=1
            time.sleep(poll_seconds)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',required=True);sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('claim');c.add_argument('--job-id',required=True);c.add_argument('--work-key',action='append',required=True);c.add_argument('--workspace',required=True);c.add_argument('--stages',required=True)
    for name in ('run','resume','_runner'):
        c=sub.add_parser(name);c.add_argument('--job-id',required=True)
    for name in ('status','collect'):
        c=sub.add_parser(name);c.add_argument('--job-id')
    c=sub.add_parser('serve');c.add_argument('--max-jobs',type=int,default=3);c.add_argument('--poll-seconds',type=float,default=2)
    c=sub.add_parser('adopt');c.add_argument('--job-id',required=True);c.add_argument('--work-key',action='append',required=True);c.add_argument('--workspace',required=True);c.add_argument('--pid',type=int,required=True);c.add_argument('--proc-start');c.add_argument('--exit-record',required=True)
    a=p.parse_args();r=Runtime(a.db)
    if a.command=='claim': value=r.claim(a.job_id,a.work_key,a.workspace,json.loads(Path(a.stages).read_text()))
    elif a.command=='adopt': value=r.adopt(a.job_id,a.work_key,a.workspace,a.pid,a.proc_start,a.exit_record)
    elif a.command=='_runner': r.run_job(a.job_id);return
    elif a.command=='serve': r.serve(a.poll_seconds,a.max_jobs);return
    else: value=getattr(r,'start' if a.command=='run' else a.command)(a.job_id)
    print(json.dumps(value,ensure_ascii=False,indent=2))
if __name__=='__main__': main()