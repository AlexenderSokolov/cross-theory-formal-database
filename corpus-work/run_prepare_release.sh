#!/usr/bin/env bash
# Prepare only reviewed bytes, then actually restore and validate a fresh local copy.
set -euo pipefail
corpus_work_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
corpus_project_root="$(dirname -- "$(dirname -- "$corpus_work_dir")")"
corpus_python="${CORPUS_PYTHON:-$corpus_project_root/runtime/python/bin/python}"
exec "$corpus_python" -B - "$corpus_work_dir" "$@" <<'PY'
from pathlib import Path
import argparse, json, os, shutil, subprocess, sys

work = Path(sys.argv[1]).resolve()
scripts = work / 'scripts'
python = sys.executable
arguments = sys.argv[2:]
if '--help' in arguments or '-h' in arguments:
    raise SystemExit(subprocess.run([python, '-B', str(scripts/'prepare_editable_release.py'), *arguments]).returncode)
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--output', type=Path, required=True)
parsed, _ = parser.parse_known_args(arguments)
output = parsed.output.absolute()
rr = subprocess.run([python, '-B', str(scripts/'prepare_editable_release.py'), *arguments], capture_output=True, text=True)
print(rr.stdout, end=''); print(rr.stderr, end='', file=sys.stderr)
if rr.returncode:
    raise SystemExit(rr.returncode)
sys.path.insert(0, str(scripts))
from corpus_delivery_tools import load, sha, local, ordinary, check_report
from prepare_editable_release import check_sql
verification = output/'verification'
if verification.exists() or verification.is_symlink():
    raise ValueError('fresh verification directory required; preserve existing files')
package = verification/'package'
reports = verification/'reports'
temporary = verification/'tmp'
package.mkdir(parents=True); reports.mkdir(); temporary.mkdir()
publication = load(output/'PUBLIC_FILELIST.json')
seen = set()
for row in publication['files']:
    if row['path'] in seen:
        raise ValueError('duplicate reviewed publication path')
    seen.add(row['path'])
    source = ordinary(local(output/'package', row['path']))
    if sha(source) != row['sha256'] or source.stat().st_size != row['bytes']:
        raise ValueError('prepared public bytes changed before verification')
    target = local(package, row['path'])
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR=str(temporary))
env['PATH'] = str(Path(python).parent) + os.pathsep + env.get('PATH', '/usr/bin:/bin')
stages = []
def run(name, args):
    command = [python, '-B', *map(str, args)]
    result = subprocess.run(command, env=env, capture_output=True, text=True)
    (reports/(name+'.stdout')).write_text(result.stdout, encoding='utf8')
    (reports/(name+'.stderr')).write_text(result.stderr, encoding='utf8')
    stages.append(dict(name=name, argv=command, exit_code=result.returncode))
    (verification/'ACTUAL_COMMANDS.json').write_text(json.dumps(stages, indent=2)+'\n')
    if result.returncode:
        print(result.stderr, end='', file=sys.stderr)
        raise SystemExit(result.returncode)
run('restore-database', [package/'restore_database.py'])
artifact_root = verification/'artifacts'
run('restore-validation-artifacts', [package/'restore_validation_artifacts.py', '--destination', artifact_root])
run('test-database', [package/'test_database.py'])
run('test-restore-database', [package/'test_restore_database.py'])
aggregate = reports/'aggregate.json'
run('actual-full-editable-gate', [scripts/'validate_corpus.py', '--mode', 'editable-delivery',
    '--package', package, '--evidence', package/'delivery-evidence.json',
    '--build-root', artifact_root/'build', '--receipt-root', artifact_root/'receipts', '--report', aggregate])
manifest = load(package/'manifest.json')
actual = check_report(aggregate, len(manifest['items']))
sql = check_sql(package, manifest)
result = dict(status='actual_local_release_SQL_artifacts_tests_fullgate_passed_not_remote',
    verified_package=str(package), verified_build_root=str(artifact_root/'build'),
    verified_receipt_root=str(artifact_root/'receipts'), actual_aggregate=actual, sql=sql,
    public_filelist_sha256=sha(output/'PUBLIC_FILELIST.json'),
    fresh_compilation_performed=False, remote_delivered_increment=0, actual_commands=stages)
(verification/'LOCAL_RESTORE_VERIFICATION.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
PY
