from pathlib import Path
import sys,os,json,socket,ssl,sqlite3
import pypdf,fitz,PIL,numpy
package=Path(sys.argv[sys.argv.index('--package')+1])
result={'python':sys.version.split()[0],'pypdf':pypdf.__version__,'fitz':fitz.VersionBind,'pillow':PIL.__version__,'numpy':numpy.__version__,
 'sqlite':sqlite3.sqlite_version,'package_writable':os.access(package,os.W_OK),'runtime_writable':os.access(Path(__file__).parent.parent/'runtime',os.W_OK),
 'personal_home_credentials_visible':any(Path(p).exists() for p in ['/disks/sata1/yupeng/.ssh','/disks/sata1/yupeng/.codex','/disks/sata1/yupeng/.git-credentials']),
 'sensitive_environment_keys_present':any(k in os.environ for k in ['OPENAI_API_KEY','CODEX_API_KEY','GH_TOKEN','GITHUB_TOKEN','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY'])}
try:
 sock=socket.socket();sock.settimeout(1);sock.connect(('1.1.1.1',443));result['network_blocked']=False
except OSError: result['network_blocked']=True
finally: sock.close()
print(json.dumps(result,indent=2))
assert not result['package_writable'] and not result['runtime_writable']
assert not result['personal_home_credentials_visible'] and not result['sensitive_environment_keys_present'] and result['network_blocked']
