"""Resumable local SSH/Git relay; all corpus preparation remains on Yupeng."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import time
import queue
import threading
import socket
from datetime import datetime, timezone
from contextlib import contextmanager
from publish_corpus_bundle import publish, GuardLost, run as git_run

PROCESS_START = datetime.now(timezone.utc).isoformat()

B = '/disks/sata1/yupeng/human-proof-corpus'
SSH = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', '-o',
       'ProxyCommand=none', '-o', 'ProxyJump=none', '-o', 'ClearAllForwardings=yes',
       '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']

def save(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(temp,path)

@contextmanager
def local_lock(root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    with (root/'pipeline.lock').open('a+b') as stream:
        stream.seek(0);stream.write(b'0');stream.flush();stream.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:yield
        finally:
            stream.seek(0)
            if os.name=='nt':msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream,fcntl.LOCK_UN)

# The fixed server stages check ownership under the existing single-writer lock.
# Their receipts are written before returning, so SSH response loss is recoverable.
PROCESS_SUPPORT = r'''
from pathlib import Path
def writer_group_members(pgid):
 members=[]
 for entry in Path('/proc').iterdir():
  if not entry.name.isdecimal():continue
  try:
   fields=(entry/'stat').read_text().split(') ',1)[1].split()
   if int(fields[2])==pgid and fields[0] not in ('Z','X'):
    members.append({'pid':int(entry.name),'start_time':fields[19]})
  except (FileNotFoundError,ProcessLookupError):continue
  except (PermissionError,IndexError,ValueError) as error:
   raise ValueError('needs_recovery: writer process group visibility unknown') from error
 return members
def external_writer_groups_terminal(record):
 if 'writer_groups' not in record:
  raise ValueError('needs_recovery: legacy stage receipt lacks child-writer terminal evidence')
 for group in record['writer_groups']:
  if writer_group_members(group['pgid']):return False
 return True
'''
REMOTE_BODY = r'''
import sys,json,subprocess,os,socket
from pathlib import Path
from contextlib import contextmanager
cfg=json.loads(sys.argv[1]);B=Path(cfg['root']);repo=B/'repo';batch=Path(cfg['batch'])
for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):os.environ.pop(key,None)
if not batch.resolve().is_relative_to((B/'operations/corpusctl/batches').resolve()):raise ValueError('batch outside fixed batch root')
state=B/'operations/corpusctl';stage=cfg['stage'];folder=batch/'controller-publish'
sys.path.insert(0,str(repo/'corpus-work/scripts'))
from corpus_control_protocol import controller_guard,load_json as load,save_json,assert_publication_guard
def save(path,value):
 with controller_guard(state,cfg['actor']):save_json(path,value)
STAGE_RECORD=None
GATE="import os,sys,json; argv=json.loads(sys.argv[1]); token=sys.stdin.buffer.read(1); sys.exit(2) if token!=b'!' else os.execvp(argv[0],argv)"
def command(argv):
 if STAGE_RECORD is None:return subprocess.check_output(argv,text=True).strip()
 from corpus_runtime import identity
 # No writer executes until its entire new process group is durably registered.
 proc=subprocess.Popen([sys.executable,'-B','-c',GATE,json.dumps(argv)],cwd=str(repo),start_new_session=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 try:
  child=identity(proc.pid)
  if not child:raise ValueError('writer launch identity unavailable')
  STAGE_RECORD['writer_groups'].append({'pgid':proc.pid,'leader':child,'argv':argv})
  save(state/'publication-external.json',STAGE_RECORD)
  out,_=proc.communicate('!')
  if proc.returncode:raise subprocess.CalledProcessError(proc.returncode,argv,out)
  return out.strip()
 except BaseException:
  if proc.poll() is None:proc.kill()
  proc.wait()
  raise
@contextmanager
def authorized_stage():
 global STAGE_RECORD
 # Publication guard prevents owner handoff; only checks/state writes take the
 # controller lock. Git copying/network operations leave admissions unblocked.
 with controller_guard(state,cfg['actor']):pass
 record=None
 if stage not in ('inspect','reconcile-external','public-result'):
  from corpus_runtime import identity
  record={'state':'running','scope':'server_stage','operation':stage,'actor':cfg['actor'],'batch_id':batch.name,'process_identity':identity(os.getpid()),'host':socket.gethostname(),'writer_groups':[]}
  STAGE_RECORD=record
  save(state/'publication-external.json',record)
 try:yield
 finally:
  if record:
   try:record['state']='terminal' if external_writer_groups_terminal(record) else 'unknown'
   except ValueError:record['state']='unknown'
   save(state/'publication-external.json',record)
   STAGE_RECORD=None
   if record['state']!='terminal':raise ValueError('needs_recovery: child writer remains live or unknown')
def git(*args):return command(['git','-C',str(repo),*args])
assert_publication_guard(state,cfg['guard_token'])
with authorized_stage():
 folder.mkdir(exist_ok=True)
 publication=batch/'publication.json'
 if publication.exists():
  pub=load(publication)
  if pub['actor']!=cfg['actor'] and pub['stage']!='reconciled':raise ValueError('publication actor transfer required')
 else:
  q=load(repo/'handoff/yupeng/PRODUCTION_QUEUE.json');active=q['active_batch'];previous=q['last_publication']
  if not active or Path(active['batch_dir']).resolve()!=batch.resolve():raise ValueError('batch is not active')
  merged=load(batch/'merge/batch-result.json')
  if merged.get('status')!='actual_editable_batch_gate_passed_not_remote' or merged.get('items')!=active['expected_count']:raise ValueError('actual merged batch required')
  proof=load(Path(previous['result_path']))
  if proof.get('verified_corpus_commit')!=previous['commit'] or proof.get('remote_main_delivered_count')!=previous['count']:raise ValueError('previous full public proof mismatch')
  remote=git('remote','get-url','origin');branch=git('branch','--show-current')
  base=git('ls-remote',remote,'refs/heads/'+branch).split()[0]
  subprocess.run(['git','-C',str(repo),'merge-base','--is-ancestor',base,'HEAD'],check=True)
  pub=dict(schema_version=2,record_type='publication',batch_id=active['batch_id'],actor=cfg['actor'],started_by=cfg['actor'],actor_history=[],stage='merged',expected_count=active['expected_count'],incoming_ids=active['incoming_ids'],remote=remote,branch=branch,expected_remote_base=base,server_parent=None,expected_tree=None,target_commit=None,bundle_path=None,previous_public_result=previous['result_path'],receipt_paths={'merge':str(batch/'merge/batch-result.json')})
  save(publication,pub)
 receipt=folder/(stage+'.json')
 if stage=='inspect':value=pub
 elif stage=='public-result':
  if pub['stage']!='reconciled':raise ValueError('publication is not reconciled')
  proof=load(Path(pub['receipt_paths']['public_result']))
  if proof.get('verified_corpus_commit')!=pub['target_commit'] or proof.get('remote_main_delivered_count')!=pub['expected_count']:raise ValueError('reconciled publication proof mismatch')
  q=load(repo/'handoff/yupeng/PRODUCTION_QUEUE.json');active=q.get('active_batch')
  same=active is not None and active['batch_id']==pub['batch_id']
  remote_count=int(q['base']['remote_main_count'])
  if remote_count<pub['expected_count'] and not same:raise ValueError('reconciled proof not counted but active batch identity changed')
  value={'public_result':proof,'queue_reconciliation_needed':same or remote_count<pub['expected_count']}
 elif stage=='reconcile-external':
  old=load(state/'publication-external.json')
  from corpus_runtime import identity
  saved=old.get('process_identity',{});live=identity(saved.get('pid',0))
  if old.get('scope')!='server_stage':raise ValueError('local external writer requires local terminal evidence')
  if live and live.get('start_time')==saved.get('start_time'):raise ValueError('needs_recovery: original server stage still running')
  if not external_writer_groups_terminal(old):raise ValueError('needs_recovery: original stage child writer still running')
  if live is None:
   old.update(state='terminal',reconciliation='server stage process terminal; resume frozen stage outputs');save(state/'publication-external.json',old)
  else:
   old.update(state='terminal',reconciliation='PID reused; original server stage terminal');save(state/'publication-external.json',old)
  value=old
 elif receipt.exists():
  value=load(receipt)
  if value.get('base')!=pub['expected_remote_base']:raise ValueError('frozen publication base mismatch')
 else:
  value={'stage':stage,'base':pub['expected_remote_base']}
  if stage=='prepared':
   prepared=load(batch/'publish/result.json')
   if prepared['verified_count']!=pub['expected_count']:raise ValueError('prepared count mismatch')
   pub['stage']='release_prepared';pub['receipt_paths']['publish']=str(batch/'publish/result.json')
  elif stage=='stage':
   if pub['stage']=='git_staged':
    if git('rev-parse','HEAD')!=pub['server_parent'] or git('write-tree')!=pub['expected_tree']:raise ValueError('staging identity changed')
    value.update(load(batch/'git-staging.json'));save(receipt,value);print(json.dumps(value));raise SystemExit(0)
   if pub['stage']!='release_prepared':raise ValueError('release must be prepared')
   # Reject unrelated staged paths before the staging helper changes the index.
   prepared=load(batch/'publish/result.json');release_root=Path(prepared.get('release_root',str(batch/'release')))
   release=load(release_root/'PUBLIC_FILELIST.json')
   allowed={'editable-corpus/'+x['path'] for x in release['files']}
   allowed.update('handoff/yupeng/main'+str(pub['expected_count'])+'/'+x for x in ('PUBLIC_FILELIST.json','batch-result.json','material-review.json'))
   allowed.update(('editable-corpus/RECOVERY_CURRENT.md','handoff/yupeng/PRODUCTION_QUEUE.json'))
   if set(git('diff','--cached','--name-only').splitlines())-allowed:raise ValueError('unrelated staged files; preserve and reconcile')
   command([str(B/'runtime/python/bin/python'),'-B',str(repo/'corpus-work/scripts/stage_corpus_release.py'),str(batch),'--owner',cfg['actor']['owner'],'--generation',str(cfg['actor']['generation']),'--guard-held','--publication-guard',cfg['guard_token'],'--project',str(B)])
   value.update(load(batch/'git-staging.json'))
   pub.update(server_parent=git('rev-parse','HEAD'),expected_tree=git('write-tree'),stage='git_staged')
   pub['receipt_paths']['stage']=str(receipt)
   # Parent/tree and batch_id are durable BEFORE any commit mutation.
   save(publication,pub)
  elif stage=='commit':
   if pub['target_commit'] is not None:
    target=pub['target_commit']
    if git('rev-parse',target+'^')!=pub['server_parent'] or git('rev-parse',target+'^{tree}')!=pub['expected_tree'] or git('log','-1','--format=%s',target)!='corpus: publish '+pub['batch_id']:raise ValueError('fixed commit recovery identity mismatch')
    value['commit']=target;save(receipt,value);print(json.dumps(value));raise SystemExit(0)
   if pub['stage']!='git_staged':raise ValueError('git_staged recovery identity required')
   staging=load(folder/'stage.json');message='corpus: publish '+pub['batch_id']
   head=git('rev-parse','HEAD')
   staged=git('diff','--cached','--name-only').splitlines()
   if head!=pub['server_parent']:
    if git('log','-1','--format=%s')!=message or git('rev-parse','HEAD^')!=pub['server_parent'] or git('rev-parse','HEAD^{tree}')!=pub['expected_tree']:raise ValueError('server HEAD changed outside frozen publication identity')
   else:
    if set(staged)-set(staging['paths']):raise ValueError('unrelated staged files; preserve and reconcile')
    if not staged or git('write-tree')!=pub['expected_tree']:raise ValueError('publication index changed; preserve and reconcile')
    git('commit','-m',message)
   value['commit']=git('rev-parse','HEAD');pub['target_commit']=value['commit']
   pub['bundle_path']=str(folder/'publication.bundle')
   pub['receipt_paths']['commit']=str(receipt)
   # commit_ready requires the actual fixed bundle; complete it in this stage.
   target=Path(pub['bundle_path']);ref='refs/corpus-publication/'+pub['batch_id']
   git('update-ref',ref,pub['target_commit'])
   if not target.exists():
    temp=folder/'publication.partial.bundle';git('bundle','create',str(temp),pub['expected_remote_base']+'..'+ref);os.replace(temp,target)
   git('bundle','verify',str(target))
   if git('bundle','list-heads',str(target)).split()[0]!=pub['target_commit']:raise ValueError('bundle target mismatch')
   pub['stage']='commit_ready';save(publication,pub)
  elif stage=='bundle':
   commit=pub['target_commit'];target=Path(pub['bundle_path'])
   git('bundle','verify',str(target))
   heads=git('bundle','list-heads',str(target)).splitlines()
   if not any(x.split()[0]==commit for x in heads):raise ValueError('bundle target mismatch')
   value.update(commit=commit,bundle=str(target),bytes=target.stat().st_size)
  elif stage=='pushed':
   if cfg['commit']!=pub['target_commit']:raise ValueError('push target mismatch')
   pub['stage']='pushed';pub['receipt_paths']['push']=cfg['receipt']
  elif stage=='verified':
   proof=load(batch/'verify-public/result.json')
   if proof.get('verified_corpus_commit')!=pub['target_commit'] or proof.get('remote_main_delivered_count')!=pub['expected_count']:raise ValueError('public proof mismatch')
   pub['stage']='reconciled';pub['receipt_paths']['public_result']=str(batch/'verify-public/result.json')
  else:raise ValueError('unknown stage')
  save(publication,pub);save(receipt,value)
 print(json.dumps(value))
'''
REMOTE = PROCESS_SUPPORT + REMOTE_BODY

GUARD = r'''
import sys,json,os
from pathlib import Path
cfg=json.loads(sys.argv[1]);state=Path(cfg['state']);os.chdir(state)
sys.path.insert(0,str(Path(cfg['root'])/'repo/corpus-work/scripts'))
from corpus_control_protocol import publication_guard,controller_guard,save_json,load_json
def start():return Path('/proc/self/stat').read_text().split(') ',1)[1].split()[19]
with publication_guard(state):
 with controller_guard(state,cfg['actor']):
  token=str(os.getpid())+'/'+start()
  save_json(state/'publication-guard.json',{'token':token,'pid':os.getpid(),'actor':cfg['actor']})
  old=load_json(state/'publication-external.json') if (state/'publication-external.json').exists() else None
 print(json.dumps({'status':'publication_guard_ready','token':token,'external':old}),flush=True)
 for line in sys.stdin:
  command=json.loads(line)
  if command['action']=='external':
   with controller_guard(state,cfg['actor']):
    record=command['record'];record.update(actor=cfg['actor'],batch_id=cfg['batch_id'],guard_token=token)
    save_json(state/'publication-external.json',record)
  print(json.dumps({'status':'guard_alive','token':token}),flush=True)
'''

class PublicationGuard:
    """An SSH stdin lifetime holds flock while local Git is an external writer."""
    def __init__(self,pipeline):
        self.pipeline=pipeline;self.messages=queue.Queue();self.last_check=0;self.token=None
    def __enter__(self):
        p=self.pipeline;cfg=dict(root=B,state=B+'/operations/corpusctl',actor=p.actor,batch_id=Path(p.a.batch).name)
        argv=SSH+[p.a.host,shlex.join([B+'/runtime/python/bin/python','-B','-c',GUARD,json.dumps(cfg)])]
        self.process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        def read():
            for line in self.process.stdout:
                try:self.messages.put(json.loads(line))
                except ValueError:self.messages.put({'status':'invalid_guard_response'})
        threading.Thread(target=read,daemon=True).start()
        try:
            message=self.messages.get(timeout=15)
            if message.get('status')!='publication_guard_ready':raise GuardLost('publication guard did not acquire lock')
            self.token=message['token'];self.previous_external=message.get('external');return self
        except BaseException as error:
            self.process.kill();self.process.wait()
            if isinstance(error,queue.Empty):raise GuardLost('publication guard startup response missing')
            raise
    def exchange(self,command):
        if self.process.poll() is not None:raise GuardLost('publication guard terminated')
        try:
            self.process.stdin.write(json.dumps(command)+'\n');self.process.stdin.flush()
            message=self.messages.get(timeout=8)
        except (OSError,queue.Empty):raise GuardLost('publication guard connection lost')
        if message.get('token')!=self.token or message.get('status')!='guard_alive':raise GuardLost('publication guard response mismatch')
    def check(self):
        if self.process.poll() is not None:raise GuardLost('publication guard terminated')
        if time.monotonic()-self.last_check>=3:
            self.exchange({'action':'ping'});self.last_check=time.monotonic()
    def external(self,record):self.exchange({'action':'external','record':record})
    def __exit__(self,*error):
        try:self.process.stdin.close()
        except OSError:pass
        try:self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:self.process.kill();self.process.wait()

class Pipeline:
    def __init__(self,args):
        self.a=args;self.actor={'owner':args.owner,'generation':args.generation}
        self.root=Path(args.cache).absolute()/Path(args.batch).name;self.root.mkdir(parents=True,exist_ok=True)
        identity={k:getattr(args,k) for k in ('batch','host')}
        path=self.root/'pipeline.json'
        if path.exists() and json.loads(path.read_text(encoding='utf-8'))!=identity:
            raise ValueError('receipt directory belongs to another publication')
        save(path,identity)

    def command(self,argv,input=None):
        env=os.environ.copy()
        for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):env.pop(k,None)
        result=subprocess.run(argv,input=input,capture_output=True,text=True,encoding='utf-8',env=env)
        if result.returncode:raise RuntimeError(result.stderr[-4000:] or result.stdout[-4000:])
        return result.stdout

    def ssh(self,argv,input=None):
        return self.command(SSH+[self.a.host,shlex.join(argv)],input)

    def step(self,name,action):
        path=self.root/(name+'.json')
        if path.exists():return json.loads(path.read_text(encoding='utf-8'))
        for attempt in range(self.a.attempts):
            try:
                if hasattr(self,'guard'):self.guard.check()
                result=action();save(path,result);return result
            except GuardLost:
                raise
            except (RuntimeError,OSError,subprocess.CalledProcessError) as error:
                save(self.root/(name+'-failure.json'),{'attempt':attempt+1,'error':str(error),'status':'retained_for_resume'})
                if attempt+1==self.a.attempts:raise
                time.sleep(self.a.retry_seconds)

    def ctl(self,action,*flags):
        # A lost SSH response is reconciled by the server's fixed stage receipts.
        out=self.ssh([B+'/repo/corpus-work/corpusctl','--controller-id',self.a.owner,'--generation',str(self.a.generation),'--publication-guard',self.guard.token,action,'--batch-dir',self.a.batch,*flags])
        return json.loads(out)

    def check_owner(self):
        out=self.ssh([B+'/repo/corpus-work/corpusctl','status','--json'])
        owner=json.loads(out)['controller']
        if {'owner':owner['owner'],'generation':owner.get('generation',0)}!=self.actor:
            raise ValueError('controller owner changed; old local publication caller rejected')

    def server(self,stage,**extra):
        self.guard.check()
        cfg=dict(root=B,batch=self.a.batch,stage=stage,actor=self.actor,guard_token=self.guard.token,**extra)
        out=self.ssh([B+'/runtime/python/bin/python','-B','-',json.dumps(cfg)],REMOTE)
        return json.loads(out.strip().splitlines()[-1])

    def transfer(self,receipt):
        dest=self.root/'publication.bundle'
        if not dest.exists() or dest.stat().st_size!=receipt['bytes']:
            temp=dest.with_suffix('.partial.bundle')
            self.command(['scp',*SSH[1:],self.a.host+':'+receipt['bundle'],str(temp)])
            if temp.stat().st_size!=receipt['bytes']:raise RuntimeError('incomplete bundle transfer')
            os.replace(temp,dest)
        # The relay validates the actual Git bundle before any push.
        return {'bundle':str(dest),'bytes':dest.stat().st_size}

    def run(self):
        self.check_owner()
        with PublicationGuard(self) as self.guard:
            pub=self.server('inspect');self.publication=pub
            if pub['stage']=='reconciled':
                completed=self.server('public-result');verified=completed['public_result']
                if completed['queue_reconciliation_needed']:
                    # Existing actual result reconciles queue only; no old batch
                    # callback is sent once a successor batch is already active.
                    verified=self.ctl('verify-public','--commit',pub['target_commit'],'--previous',pub['previous_public_result'])
                save(self.root/'result.json',verified)
                return verified
            self.reconcile_external(pub)
            self.step('publish',lambda:self.ctl('publish'))
            self.step('prepared',lambda:self.server('prepared'))
            self.step('stage',lambda:self.server('stage'))
            self.step('commit',lambda:self.server('commit'))
            pub=self.server('inspect');self.publication=pub;commit=pub['target_commit']
            bundle=self.step('bundle',lambda:self.server('bundle'))
            local=self.step('scp',lambda:self.transfer(bundle))
            pushed=self.step('push',lambda:self.push(local['bundle'],pub))
            if pushed['commit']!=commit:raise ValueError('push target differs from frozen server commit')
            self.step('pushed',lambda:self.server('pushed',commit=commit,receipt=str(self.root/'push.json')))
            verified=self.step('verify-public',lambda:self.ctl('verify-public','--commit',commit,'--previous',pub['previous_public_result']))
            if verified.get('verified_corpus_commit')!=commit or verified.get('remote_main_delivered_count')!=pub['expected_count']:
                raise ValueError('public restoration did not verify exact commit and delivered count')
            self.step('verified',lambda:self.server('verified'))
            save(self.root/'result.json',verified)
            return verified

    def reconcile_external(self,pub):
        previous=self.guard.previous_external
        if not previous or previous.get('state') not in ('running','unknown'):return
        if previous.get('scope')=='server_stage':
            self.server('reconcile-external');return
        local=self.root/'external-write.json'
        record=json.loads(local.read_text(encoding='utf-8')) if local.exists() else {}
        if record.get('process_identity')!=previous.get('process_identity') or not (record.get('writer_terminal') or record.get('state')=='terminal'):
            raise ValueError('needs_recovery: prior external writer terminal evidence required; remote base alone is insufficient')
        heads=git_run(['git','-c','http.proxy=','ls-remote',pub['remote'],'refs/heads/'+pub['branch']]).split()
        if not heads:raise ValueError('remote branch missing while reconciling external write')
        record.update(state='terminal',remote_commit=heads[0],reconciled_at=datetime.now(timezone.utc).isoformat())
        self.guard.external(record);save(local,record)
        if heads[0] not in (pub['expected_remote_base'],pub['target_commit']):
            raise ValueError('remote advanced; preserve and integrate before continuing publication')

    def push(self,bundle,pub):
        # Persist the local publisher identity before initiating an external write.
        record={'state':'running','process_identity':{'host':socket.gethostname(),'pid':os.getpid(),'started_at':PROCESS_START},'target_commit':pub['target_commit'],'started_at':datetime.now(timezone.utc).isoformat()}
        save(self.root/'external-write.json',record);self.guard.external(record)
        try:
            result=publish(bundle,self.a.relay,pub['branch'],pub['expected_remote_base'],pub['remote'],pub['target_commit'],self.guard.check)
            record.update(state='terminal',result=result,finished_at=datetime.now(timezone.utc).isoformat())
            save(self.root/'external-write.json',record);self.guard.external(record)
            return result
        except BaseException as error:
            # A lost guard prevents shared writes; local evidence is retained.
            record.update(state='unknown',writer_terminal=True,error=str(error),finished_at=datetime.now(timezone.utc).isoformat())
            save(self.root/'external-write.json',record)
            try:self.guard.external(record)
            except GuardLost:pass
            raise

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['publish-batch'])
    for name in ('batch','relay','cache','host','owner'):p.add_argument('--'+name,required=True)
    p.add_argument('--generation',type=int,required=True)
    p.add_argument('--attempts',type=int,default=3);p.add_argument('--retry-seconds',type=float,default=15)
    a=p.parse_args()
    if a.attempts<1 or a.retry_seconds<0:p.error('positive attempts and nonnegative retry interval required')
    with local_lock(Path(a.cache)/Path(a.batch).name):
        print(json.dumps(Pipeline(a).run(),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
