"""Prepare an exact public filelist from proven old cache bytes and commit raw URLs.

Transport only: no SQL restore, artifact restore, compilation, gate or admission.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import os
import time
import urllib.error
import urllib.parse
import urllib.request

REPOSITORY = 'AlexenderSokolov/cross-theory-formal-database'
PREFIX = 'editable-corpus'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def pin(value, size=64):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{' + str(size) + '}', value):
        raise ValueError('external identity must be lowercase hexadecimal: ' + str(size))
    return value


def no_symlinks(path):
    path = Path(path).absolute()
    for node in (path, *path.parents):
        if node.is_symlink():
            raise ValueError('symlink path rejected: ' + str(node))
    return path


def ordinary(path):
    path = no_symlinks(path)
    if not path.is_file():
        raise ValueError('ordinary file required, not directory or absent path: ' + str(path))
    return path


def strict_load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(ordinary(path).read_text(encoding='utf8'), object_pairs_hook=unique)


def checked_json(path, expected):
    if digest(ordinary(path)) != pin(expected):
        raise ValueError('external pin mismatch: ' + str(path))
    return strict_load(path)


def canonical_path(name):
    if not isinstance(name, str) or not name or any(c in name for c in '\\:%?#\x00\r\n') or any(ord(c) < 32 for c in name):
        raise ValueError('noncanonical filelist path')
    pure = PurePosixPath(name)
    if pure.is_absolute() or pure.as_posix() != name or any(p in ('', '.', '..') for p in name.split('/')):
        raise ValueError('noncanonical filelist path: ' + name)
    return name


def filelist(path, expected):
    data = checked_json(path, expected)
    if data.get('schema_version') != 1 or not isinstance(data.get('files'), list) or not data['files']:
        raise ValueError('explicit nonempty schema1 filelist required')
    entries = {}
    for row in data['files']:
        if not isinstance(row, dict):
            raise ValueError('filelist entry must be object')
        name = canonical_path(row.get('path'))
        if name in entries:
            raise ValueError('duplicate filelist path: ' + name)
        if type(row.get('bytes')) is not int or row['bytes'] < 0:
            raise ValueError('exact nonnegative file bytes required')
        pin(row.get('sha256'))
        entries[name] = row
    for name in entries:
        if any(str(parent) in entries for parent in PurePosixPath(name).parents if str(parent) != '.'):
            raise ValueError('file/directory prefix collision: ' + name)
    return entries


def verified_previous(proof_path, proof_pin, old_commit, old_filelist_pin, old_entries, cache, test=False):
    proof = checked_json(proof_path, proof_pin)
    if proof.get('verified_corpus_commit') != pin(old_commit, 40) or proof.get('public_filelist_sha256') != old_filelist_pin:
        raise ValueError('old public proof commit/filelist mismatch')
    if test:
        if proof.get('status') != 'test_local_fixture_previous_bytes_only_not_public' or proof.get('cache_root') != str(cache):
            raise ValueError('explicit test-local-fixture proof required')
        if proof.get('public_files_verified') != len(old_entries):
            raise ValueError('test fixture file count mismatch')
        return proof
    status = proof.get('status', '')
    if not (re.fullmatch(r'public_exact_commit_full[1-9][0-9]*_restored_verified', status) or
            re.fullmatch(r'exact_public_commit_complete_main[1-9][0-9]*_SQL_and_artifactchain_recovery_verified', status)):
        raise ValueError('actual exact public full-restoration proof required; test/prepared/local evidence is insufficient')
    count = proof.get('remote_main_delivered_count')
    if type(count) is not int or count <= 0 or proof.get('public_files_verified', proof.get('public_files')) != len(old_entries):
        raise ValueError('old actual proof count mismatch')
    sql = proof.get('sql', {})
    if sql.get('problem_count') != count or sql.get('integrity') != 'ok' or sql.get('foreign_key_errors') != [] or sql.get('full_problem_and_source_projection') is not True:
        raise ValueError('old actual full SQL proof required')
    pin(sql.get('sqlite_sha256'))
    commands = proof.get('commands', [])
    if len(commands) != 5 or any(c.get('returncode') != 0 for c in commands):
        raise ValueError('five successful actual restoration command records required')
    for record in commands:
        if digest(ordinary(record.get('log'))) != pin(record.get('log_sha256')):
            raise ValueError('old actual command log pin mismatch')
    for index, script in enumerate(('restore_database.py', 'test_restore_database.py', 'test_database.py')):
        args = commands[index].get('argv', [])
        if len(args) < 3 or Path(args[2]) != cache / script:
            raise ValueError('old actual command/cache root mismatch')
    if Path(commands[3]['argv'][2]).name not in ('restore_validation_artifacts.py', 'restore_validation_chain.py', 'resume_validation_chain.py'):
        raise ValueError('old actual artifact restoration command required')
    args = commands[4].get('argv', [])
    def arg(name):
        if args.count(name) != 1 or args.index(name) + 1 >= len(args):
            raise ValueError('old aggregate command scope missing: ' + name)
        return args[args.index(name) + 1]
    if arg('--mode') != 'editable-delivery' or arg('--package') != str(cache) or arg('--evidence') != str(cache / 'delivery-evidence.json') or '--item' in args:
        raise ValueError('old actual complete gate/cache scope mismatch')
    gate_pin = proof.get('actual_gate', proof.get('aggregate'))
    if not isinstance(gate_pin, dict) or gate_pin.get('actual_qualified_count') != count:
        raise ValueError('old actual complete gate proof required')
    gate = checked_json(gate_pin['report'], gate_pin['sha256'])
    if gate.get('mode') != 'editable-delivery' or gate.get('editable_qualified_count') != count or gate.get('package_item_count') != count or gate.get('errors') != [] or len(gate.get('items', {})) != count or any(v.get('errors') != [] for v in gate['items'].values()):
        raise ValueError('old actual full aggregate gate failed or incomplete')
    if gate.get('receipt_set') != arg('--receipt-root'):
        raise ValueError('old gate receipt root mismatch')
    manifest = old_entries.get('manifest.json')
    if not manifest or (proof.get('manifest_sha256') is not None and proof['manifest_sha256'] != manifest['sha256']):
        raise ValueError('old proof/filelist manifest identity mismatch')
    return proof


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        raise urllib.error.HTTPError(request.full_url, code, 'exact commit URL redirect rejected', headers, fp)


def raw_url(commit, name, test_local_http=None):
    pin(commit, 40)
    canonical_path(name)
    base = 'https://raw.githubusercontent.com'
    if test_local_http is not None:
        parsed = urllib.parse.urlsplit(test_local_http)
        if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or parsed.username or parsed.password or
                parsed.path or parsed.query or parsed.fragment or not parsed.port or test_local_http != 'http://127.0.0.1:' + str(parsed.port)):
            raise ValueError('test HTTP must be explicit canonical loopback URL http://127.0.0.1:PORT')
        base = test_local_http
    return base + '/' + REPOSITORY + '/' + commit + '/' + PREFIX + '/' + urllib.parse.quote(name, safe='/')


def complete(path, row):
    return path.is_file() and not path.is_symlink() and path.stat().st_size == row['bytes'] and digest(path) == row['sha256']


def download(url, row, target, attempts=4, retry_seconds=2):
    """Atomic per-file retries; leave partial bytes for diagnosis, never accept them."""
    target = no_symlinks(target)
    if complete(target, row):
        return row['bytes']
    partial = no_symlinks(target.with_name(target.name + '.transport-partial'))
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(url, headers={'User-Agent': 'human-proof-corpus-explicit-filelist-transport/1'})
    for attempt in range(attempts):
        try:
            total = 0
            h = hashlib.sha256()
            with opener.open(request, timeout=60) as response:
                if response.geturl() != url or response.status != 200:
                    raise ValueError('noncanonical or failed exact URL response')
                with partial.open('wb') as stream:
                    while True:
                        block = response.read(min(1024 * 1024, row['bytes'] + 1 - total))
                        if not block:
                            break
                        stream.write(block); h.update(block); total += len(block)
                        if total > row['bytes']:
                            raise ValueError('download exceeds externally declared size')
            if total != row['bytes'] or h.hexdigest() != row['sha256']:
                raise ValueError('download size/SHA mismatch: ' + row['path'])
            os.replace(partial, target)
            return total
        except (OSError, urllib.error.URLError, ValueError) as error:
            if isinstance(error, urllib.error.HTTPError) and error.code not in (408, 429, 500, 502, 503, 504):
                raise
            if attempt + 1 == attempts:
                raise
            time.sleep(retry_seconds * (attempt + 1))


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def prepare(commit, current_filelist, current_pin, cache, old_filelist, old_pin,
            old_public_proof, old_proof_pin, old_commit, output, test_local_http=None, attempts=4, retry_seconds=2):
    if attempts < 1 or retry_seconds < 0:
        raise ValueError('positive attempts and nonnegative retry interval required')
    commit, old_commit = pin(commit, 40), pin(old_commit, 40)
    cache, output = no_symlinks(cache), no_symlinks(output)
    if not cache.is_dir():
        raise ValueError('actual previous restoration cache directory required')
    if output.resolve().is_relative_to(cache.resolve()):
        raise ValueError('output cannot be inside old actual cache')
    current = filelist(current_filelist, current_pin)
    old = filelist(old_filelist, old_pin)
    verified_previous(old_public_proof, old_proof_pin, old_commit, old_pin, old, cache, test_local_http is not None)
    # Validate URL authority before creating output even if all rows will reuse cache.
    raw_url(commit, next(iter(current)), test_local_http)
    reuse = {name for name, row in current.items() if name in old and (row['bytes'], row['sha256']) == (old[name]['bytes'], old[name]['sha256'])}
    for name in sorted(reuse):
        source = ordinary(cache / name)
        if source.stat().st_size != current[name]['bytes'] or digest(source) != current[name]['sha256']:
            raise ValueError('proven old cache bytes changed: ' + name)
    package = no_symlinks(output / 'package')
    receipt_path = output / 'TRANSPORT_RECEIPT.json'
    ledger_path = output / 'TRANSFER_LEDGER.jsonl'
    receipt = {'status': 'transport_in_progress_not_restored_or_qualified', 'repository': REPOSITORY, 'current_commit': commit,
        'current_filelist_sha256': current_pin, 'old_commit': old_commit, 'old_filelist_sha256': old_pin,
        'old_public_proof_sha256': old_proof_pin, 'old_cache': str(cache), 'package': str(package),
        'test_local_http_fixture': test_local_http is not None, 'files_declared': len(current), 'files_completed': 0,
        'reused_files': 0, 'downloaded_files': 0, 'reused_bytes': 0, 'downloaded_bytes': 0,
        'actual_SQL_or_artifact_restore_performed': False, 'actual_full_gate_performed': False,
        'fresh_compilation_performed': False, 'remote_count_increment': 0,
        'next_action': 'Root must independently pin current source/program/helper identities, actually restore SQL/artifact chain and execute full gate before any delivered-count claim.'}
    if receipt_path.exists():
        previous = strict_load(receipt_path)
        for key in ('repository', 'current_commit', 'current_filelist_sha256', 'old_commit',
                    'old_filelist_sha256', 'old_public_proof_sha256', 'old_cache', 'package', 'test_local_http_fixture'):
            if previous.get(key) != receipt[key]:
                raise ValueError('resume transport identity mismatch: ' + key)
    elif output.exists() and any(output.iterdir()):
        if set(output.iterdir()) != {package} or any(package.iterdir()):
            raise ValueError('existing output has no matching transport receipt')
    output.mkdir(parents=True, exist_ok=True)
    package.mkdir(exist_ok=True)
    dump(receipt_path, receipt)
    try:
        shutil.copy2(ordinary(current_filelist), output / 'PUBLIC_FILELIST.json')
        if digest(output / 'PUBLIC_FILELIST.json') != current_pin:
            raise ValueError('externally pinned filelist changed during copy')
        with ledger_path.open('w', encoding='utf8') as ledger:
            for name, row in sorted(current.items()):
                target = package / name
                target.parent.mkdir(parents=True, exist_ok=True)
                already_complete = complete(target, row)
                if name in reuse:
                    if not already_complete:
                        shutil.copy2(ordinary(cache / name), target)
                    if target.stat().st_size != row['bytes'] or digest(target) != row['sha256']:
                        raise ValueError('cache changed during copy: ' + name)
                    action, url = 'reuse_copy2_old_public_proven_bytes', None
                    receipt['reused_files'] += 1
                    receipt['reused_bytes'] += row['bytes']
                else:
                    url = raw_url(commit, name, test_local_http)
                    if not already_complete:
                        download(url, row, target, attempts, retry_seconds)
                    action = 'download_test_local_http_fixture' if test_local_http else 'download_exact_public_commit_raw'
                    receipt['downloaded_files'] += 1
                    receipt['downloaded_bytes'] += row['bytes']
                ledger.write(json.dumps({'path': name, 'bytes': row['bytes'], 'sha256': row['sha256'], 'action': action, 'resumed_verified_existing': already_complete, 'exact_url': url}) + '\n')
                ledger.flush()
                receipt['files_completed'] += 1
        receipt['ledger_sha256'] = digest(ledger_path)
        receipt['status'] = ('prepared_test_local_transport_fixture_not_public' if test_local_http else
                             'prepared_exact_public_transport_requires_actual_restore_and_full_gate')
        dump(receipt_path, receipt)
    except Exception as error:
        receipt.update(status='failed_transport_partial_output_retained_not_qualified', failure_type=type(error).__name__, failure=str(error))
        if ledger_path.exists():
            receipt['ledger_sha256'] = digest(ledger_path)
        dump(receipt_path, receipt)
        raise
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('commit', 'filelist-sha256', 'old-filelist-sha256', 'old-public-proof-sha256', 'old-commit'):
        parser.add_argument('--' + name, required=True)
    for name in ('filelist', 'cache', 'old-filelist', 'old-public-proof', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--attempts', type=int, default=4)
    parser.add_argument('--retry-seconds', type=float, default=2)
    parser.add_argument('--test-local-http', help='Explicit synthetic fixture mode only; never public restoration evidence')
    args = parser.parse_args()
    result = prepare(args.commit, args.filelist, args.filelist_sha256, args.cache, args.old_filelist,
                     args.old_filelist_sha256, args.old_public_proof, args.old_public_proof_sha256,
                     args.old_commit, args.output, args.test_local_http, args.attempts, args.retry_seconds)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
