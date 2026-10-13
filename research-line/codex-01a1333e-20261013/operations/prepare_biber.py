from pathlib import Path
import os, shutil, subprocess, tarfile, urllib.request
P = Path(__file__).resolve().parent.parent
runtime = P / '.work' / 'biber-2.21'
binary = runtime / 'bin' / 'biber'
url = 'https://downloads.sourceforge.net/project/biblatex-biber/biblatex-biber/2.21/binaries/Linux/biber-linux_x86_64.tar.gz'
runtime.mkdir(parents=True, exist_ok=True)
tmp = runtime / 'tmp'
tmp.mkdir(exist_ok=True)
env = os.environ.copy()
env['TMPDIR'] = str(tmp)
env['PAR_GLOBAL_TMPDIR'] = str(tmp)
if not binary.is_file():
    archive = runtime / 'biber-linux_x86_64.tar.gz'
    if not archive.is_file():
        partial = runtime / 'biber-linux_x86_64.tar.gz.partial'
        with urllib.request.urlopen(url, timeout=60) as response, partial.open('wb') as output:
            shutil.copyfileobj(response, output)
        partial.rename(archive)
    with tarfile.open(archive, 'r:gz') as package:
        matches = [m for m in package.getmembers() if m.isfile() and Path(m.name).name == 'biber']
        if len(matches) != 1:
            raise RuntimeError('Official archive must contain one regular biber executable')
        binary.parent.mkdir(exist_ok=True)
        with package.extractfile(matches[0]) as source, binary.open('wb') as output:
            shutil.copyfileobj(source, output)
    binary.chmod(0o755)
result = subprocess.run([str(binary), '--version'], env=env, check=True, capture_output=True, text=True)
if '2.21' not in result.stdout:
    raise RuntimeError('Expected Biber 2.21, got: ' + result.stdout)
print(result.stdout.strip())
print('Private Biber ready:', binary)
