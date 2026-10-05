"""Push a server-produced incremental bundle using the controller's Git identity."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import uuid

def run(args, cwd=None):
    env=os.environ.copy()
    for k in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):
        env.pop(k,None)
    return subprocess.run(args,cwd=cwd,env=env,check=True,capture_output=True,text=True).stdout.strip()

def publish(bundle, relay, branch, expected_base, remote):
    relay=Path(relay).absolute();bundle=Path(bundle).absolute()
    if not bundle.is_file(): raise ValueError('bundle missing')
    if not relay.exists(): run(['git','init','--bare',str(relay)])
    git=['git','-c','http.proxy=','--git-dir='+str(relay)]
    run(git+['check-ref-format','refs/heads/'+branch])
    # Acquire the actual public ancestor before checking an incremental bundle.
    heads=run(git+['ls-remote',remote,'refs/heads/'+branch]).split()
    if not heads: raise ValueError('remote branch missing')
    current=heads[0]
    run(git+['fetch',remote,'refs/heads/'+branch+':refs/remotes/publish-base/'+branch])
    run(git+['bundle','verify',str(bundle)])
    incoming='refs/corpus-publish/'+uuid.uuid4().hex
    run(git+['fetch',str(bundle),'HEAD:'+incoming])
    target=run(git+['rev-parse',incoming])
    if current==target:
        return {'status':'already_pushed_requires_public_restore','commit':target,'branch':branch}
    if current!=expected_base:
        raise ValueError('remote advanced; preserve it and integrate on server before publishing')
    run(git+['merge-base','--is-ancestor',current,target])
    paths=run(git+['diff','--name-only',current,target]).splitlines()
    run(git+['push',remote,target+':refs/heads/'+branch])
    verified=run(git+['ls-remote',remote,'refs/heads/'+branch]).split()[0]
    if verified!=target: raise ValueError('remote branch changed after push; reconcile exact commit')
    return {'status':'normal_push_verified_requires_public_restore','commit':target,'previous_commit':current,
            'branch':branch,'changed_paths':paths,'remote_count_increment':0}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle',required=True);p.add_argument('--relay',required=True)
    p.add_argument('--branch',default='corpus-progress-20261001')
    p.add_argument('--expected-base',required=True)
    p.add_argument('--remote',default='https://github.com/AlexenderSokolov/cross-theory-formal-database.git')
    p.add_argument('--receipt',required=True)
    a=p.parse_args();result=publish(a.bundle,a.relay,a.branch,a.expected_base,a.remote)
    Path(a.receipt).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
