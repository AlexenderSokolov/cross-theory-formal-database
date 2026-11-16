"""Acquire complete author works, without selecting or qualifying problems (Python 3.9+)."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import json
import gzip
import os
from collections import Counter
from functools import lru_cache
import subprocess
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tarfile
import threading
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
import zipfile

ATTACHMENTS = ('.tex', '.bib', '.bbl', '.bst', '.sty', '.cls', '.png', '.jpg', '.jpeg', '.pdf', '.zip', '.tar', '.tar.gz', '.tgz', '.eps', '.ps', '.svg', '.tikz', '.dat', '.csv', '.def')

# Verified CTAN distribution packages; absence is runtime readiness, not author material loss.
REGISTERED_RUNTIME_PACKAGES = {name + '.sty': 'https://ctan.org/pkg/' + name
                               for name in ('ccicons', 'hyperxmp', 'lastpage', 'mathdots',
                                            'epigraph', 'fourier', 'lettrine', 'endnotes', 'epsf', 'footmisc')}
# CTAN's newtx bundle explicitly supplies these two differently named styles.
REGISTERED_RUNTIME_PACKAGES.update({name + '.sty': 'https://ctan.org/pkg/newtx'
                                    for name in ('newtxmath', 'newtxtext')})

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Held(Exception):
    pass

def work_directory(key):
    value = re.sub(r'[^\w.-]+', '-', key, flags=re.UNICODE).strip('.-')
    if not value or value.upper().split('.')[0] in {'CON','PRN','AUX','NUL', *('COM%d'%i for i in range(1,10)), *('LPT%d'%i for i in range(1,10))}:
        raise ValueError('work_key cannot form a safe directory')
    return value[:180]

def relative_path(name):
    name = unquote(name).replace('\\', '/')
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or any(':' in part for part in path.parts):
        raise ValueError('unsafe source path: ' + name)
    return Path(*path.parts)

def checked_copy(source, output, check_space, *, remaining_bytes=0):
    copied = 0
    while True:
        block = source.read(1024 * 1024)
        if not block:
            return copied
        if check_space:
            check_space(max(len(block), remaining_bytes))
        output.write(block)
        copied += len(block)
        remaining_bytes = max(0, remaining_bytes - len(block))


def extract_archive(archive, destination, check_space=None):
    """Validate every member and its full remaining size before target creation."""
    destination = Path(destination)
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as stream:
            members = stream.infolist()
            for member in members:
                relative_path(member.filename)
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode))):
                    raise ValueError('unsafe zip member: ' + member.filename)
            remaining = sum(member.file_size for member in members if not member.is_dir())
            if check_space:check_space(remaining)
            destination.mkdir(parents=True, exist_ok=True)
            for member in members:
                target = destination / relative_path(member.filename)
                if check_space:check_space(remaining)
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with stream.open(member) as source, target.open('wb') as output:
                        copied = checked_copy(source, output, check_space, remaining_bytes=remaining)
                    remaining = max(0, remaining - copied)
    else:
        with tarfile.open(archive) as stream:
            members = stream.getmembers()
            for member in members:
                relative_path(member.name)
                if not (member.isfile() or member.isdir()):
                    raise ValueError('unsafe tar member: ' + member.name)
            remaining = sum(member.size for member in members if member.isfile())
            if check_space:check_space(remaining)
            destination.mkdir(parents=True, exist_ok=True)
            for member in members:
                target = destination / relative_path(member.name)
                if check_space:check_space(remaining)
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with stream.extractfile(member) as source, target.open('wb') as output:
                        copied = checked_copy(source, output, check_space, remaining_bytes=remaining)
                    remaining = max(0, remaining - copied)

def host_family(url):
    hostname = (urlsplit(url).hostname or '').lower().rstrip('.')
    return 'arxiv.org' if hostname == 'arxiv.org' or hostname.endswith('.arxiv.org') else hostname


@lru_cache(maxsize=512)
def tex_runtime_file(name):
    standard = {'article.cls','report.cls','book.cls','amsart.cls','amsbook.cls','amsproc.cls',
                'amsmath.sty','amssymb.sty','amsthm.sty','graphicx.sty','graphics.sty','xcolor.sty',
                'color.sty','hyperref.sty','geometry.sty','fontenc.sty','inputenc.sty','babel.sty',
                'mathtools.sty','mathrsfs.sty','latexsym.sty','bm.sty','array.sty','longtable.sty',
                'tikz.sty','pgfplots.sty','enumerate.sty','enumitem.sty','url.sty','cite.sty',
                'natbib.sty','biblatex.sty','ifpdf.sty','iftex.sty','microtype.sty','fancyhdr.sty',
                'booktabs.sty','float.sty','caption.sty','subcaption.sty','subfig.sty','verbatim.sty',
                'plain.bst','alpha.bst','abbrv.bst','unsrt.bst','amsplain.bst','amsalpha.bst','plainnat.bst','abbrvnat.bst','unsrtnat.bst',
                'amstex.tex','plain.tex','eplain.tex','epsf.tex','glyphtounicode.tex'}
    if name in standard:
        return True
    if not Path(name).suffix:
        return False
    tool = shutil.which('kpsewhich')
    if tool:
        result = subprocess.run([tool, name], capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and bool(result.stdout.strip())
    return False


def unpack_native_source(target, kind, check_space, advisories, *, attachment=False):
    """Keep the received original; handle tar/ZIP or arXiv's single gzip/TeX source."""
    with target.open('rb') as stream:
        prefix = stream.read(1024).lstrip().lower()
    if prefix.startswith((b'<!doctype html', b'<html')):
        raise ValueError('source endpoint returned HTML instead of native source')
    if prefix.startswith(b'%pdf'):
        if attachment and target.suffix.lower() == '.pdf':
            return
        raise ValueError('source endpoint returned PDF instead of native source')
    if zipfile.is_zipfile(target) or tarfile.is_tarfile(target):
        extract_archive(target, target.parent / (target.name + '.extracted'), check_space)
        return
    if kind != 'arxiv':
        if kind == 'archive':
            raise ValueError('archive URL did not return a supported archive')
        return
    destination = target.parent / (target.name + '.extracted')
    if check_space:check_space(max(UNKNOWN_INPUT_BYTES, target.stat().st_size))
    destination.mkdir()
    if prefix.startswith(b'\x1f\x8b'):
        filename = None
        with target.open('rb') as header:
            fixed = header.read(10)
            if len(fixed) != 10:
                raise ValueError('truncated gzip source')
            flags = fixed[3]
            if flags & 4:
                extra = int.from_bytes(header.read(2), 'little'); header.read(extra)
            if flags & 8:
                raw = bytearray()
                for _ in range(4096):
                    byte = header.read(1)
                    if not byte or byte == b'\0': break
                    raw.extend(byte)
                else: raise ValueError('gzip source filename too long')
                filename = relative_path(raw.decode('latin-1')) if raw else None
        relative = filename if filename and filename.suffix == '.tex' else Path('source.tex')
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(target, 'rb') as source, output.open('wb') as stream:
            checked_copy(source, stream, check_space)
    else:
        output = destination / 'source.tex'
        if check_space:check_space(target.stat().st_size)
        with target.open('rb') as source, output.open('wb') as stream:
            checked_copy(source, stream, check_space, remaining_bytes=target.stat().st_size)
    with output.open('rb') as stream:
        body = stream.read(65536)
    if body.lstrip().startswith(b'%PDF') or not re.search(br'\\(?:documentclass|documentstyle|begin|input|def|newcommand)\b', body):
        raise ValueError('arXiv response is not identified as native TeX')
    advisories.append('single_native_tex_preserved: ' + str(output.relative_to(target.parent)))


def visible_attachments(row, landing_url, content):
    parser = Links(); parser.feed(content)
    origin = urlsplit(landing_url)
    doi = re.search(r'10\.5802/[a-z]+\.\d+', landing_url + ' ' + row['source_url'])
    scoped = bool(doi or re.search(r'/(?:Volumes|conf-proc)/\d+/', origin.path) or 'sigma-journal.com' in origin.netloc)
    prefix = '/article/' + doi.group(0) + '/file/' if doi else origin.path.rsplit('/', 1)[0] + '/'
    primary_stem = Path(urlsplit(row['source_url']).path).stem
    for link, tag in parser.links:
        url = urljoin(landing_url, link); parts = urlsplit(url)
        if parts.netloc != origin.netloc or not parts.path.lower().endswith(ATTACHMENTS):continue
        if scoped and not parts.path.startswith(prefix):continue
        figure = bool(re.search(r'(?:^|/)(?:fig(?:ure)?s?|images?|graphics)(?:/|[-_0-9])', parts.path, re.I))
        if parts.path.lower().endswith('.pdf'):
            if doi and not figure:continue
            if not scoped and not figure:continue
            if Path(parts.path).stem == primary_stem:continue
        yield url


def selected_file_branches(text, tex, root, advisories):
    """Select only literal IfFileExists branches; leave dynamic conditions unresolved."""
    def group(position):
        while position < len(text) and text[position].isspace():position += 1
        if position >= len(text) or text[position] != '{':return None
        start = position + 1
        depth = 1
        position = start
        while position < len(text):
            if text[position] == '\\':
                position += 2
                continue
            if text[position] == '{':depth += 1
            elif text[position] == '}':
                depth -= 1
                if depth == 0:return text[start:position], position + 1
            position += 1
        return None

    output = []
    cursor = 0
    for match in re.finditer(r'\\IfFileExists\b', text):
        if match.start() < cursor:continue
        output.append(text[cursor:match.start()])
        groups = []
        position = match.end()
        for _ in range(3):
            parsed = group(position)
            if parsed is None:break
            value, position = parsed
            groups.append(value)
        label = str(tex.relative_to(root))
        if len(groups) != 3:
            advisories.append('unresolved_dynamic_dependency: ' + label + ': malformed IfFileExists')
            # Never interpret malformed branches as mandatory dependencies.
            cursor = len(text)
            break
        name, yes, no = groups
        name = name.strip()
        if not name or any(character in name for character in ('\\', '#', '{', '}', ':')) or Path(name).is_absolute():
            advisories.append('unresolved_dynamic_dependency: ' + label + ': IfFileExists ' + name)
        else:
            bases = [tex.parent] + list(tex.parent.parents)
            found = any((base / name).resolve().is_relative_to(root) and (base / name).is_file()
                        for base in bases if base.is_relative_to(root))
            if not found:
                tool = shutil.which('kpsewhich')
                if tool:
                    result = subprocess.run([tool, name], capture_output=True, text=True, timeout=10)
                    found = result.returncode == 0 and bool(result.stdout.strip())
            branch = yes if found else no
            output.append(selected_file_branches(branch, tex, root, advisories))
        cursor = position
    output.append(text[cursor:])
    return ''.join(output)


def missing_materials(root, advisories=None):
    root = Path(root).resolve()
    missing = []
    advisories = advisories if advisories is not None else []
    runtime_inputs = {'glyphtounicode', 'plain', 'eplain', 'epsf', 'supp-pdf', 'supp-pdf.mkii', 'pdftexconfig', 'amsmath', 'amssymb'}

    def contained_file(path):
        resolved = path.resolve()
        return resolved.is_relative_to(root) and resolved.is_file()

    for tex in (p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in ('.tex', '.sty', '.cls')):
        text = re.sub(r'(?<!\\)%[^\n]*', '', tex.read_text(encoding='utf-8', errors='replace'))
        text = selected_file_branches(text, tex, root, advisories)
        commands = re.findall(r'\\(bibliography|bibliographystyle|addbibresource|input|include|includegraphics|usepackage|RequirePackage|documentclass|documentstyle|LoadClass)\*?(?:\[[^\]]*\])?\s*\{([^}]+)\}', text)
        commands += re.findall(r'\\(input|include)\s+([^\s{}%\\]+)', text)
        for command, argument in commands:
            for name in argument.split(','):
                name = name.strip()
                label = str(tex.relative_to(root)) + ': ' + name
                if '\\' in name or '#' in name:
                    advisories.append('unresolved_dynamic_dependency: ' + label)
                    continue
                if command == 'input' and name.removesuffix('.tex') in runtime_inputs:
                    advisories.append('tex_runtime_dependency: ' + label)
                    continue
                suffixes = {'bibliography':['.bib'], 'bibliographystyle':['.bst'], 'addbibresource':['.bib'], 'input':['.tex'], 'include':['.tex'], 'includegraphics':['.pdf','.png','.jpg','.jpeg','.eps'], 'usepackage':['.sty'], 'RequirePackage':['.sty'], 'documentclass':['.cls'], 'documentstyle':['.sty','.cls'], 'LoadClass':['.cls']}[command]
                relative = Path(name)
                if relative.is_absolute() or ':' in name:
                    missing.append(label)
                    continue
                candidates = [relative] + [Path(str(relative) + suffix) for suffix in suffixes]
                bases = []
                base = tex.parent
                while base.is_relative_to(root):
                    bases.append(base)
                    if base == root:
                        break
                    base = base.parent
                if command == 'includegraphics':
                    for group in re.findall(r'\\graphicspath\s*\{((?:\s*\{[^}]*\})+)\s*\}', text):
                        for folder in re.findall(r'\{([^}]*)\}', group):
                            if '\\' in folder or '#' in folder:
                                advisories.append('unresolved_dynamic_dependency: ' + str(tex.relative_to(root)) + ': ' + folder)
                            else:
                                bases.extend([base / folder for base in list(bases)])
                found = any(contained_file(base / candidate) for base in bases for candidate in candidates)
                retained_bbl = tex.with_suffix('.bbl')
                if command in ('bibliography', 'bibliographystyle', 'addbibresource') and retained_bbl.is_file() and retained_bbl.stat().st_size > 0:
                    found = True
                    advisories.append('retained_bibliography_output: ' + label)
                if not found and command in ('input', 'usepackage', 'RequirePackage', 'documentclass', 'documentstyle', 'LoadClass', 'bibliographystyle'):
                    if any(tex_runtime_file(str(candidate)) for candidate in candidates):
                        advisories.append('tex_runtime_dependency: ' + label)
                        found = True
                if not found and command in ('usepackage', 'RequirePackage'):
                    registered = next((str(candidate) for candidate in candidates
                                       if str(candidate) in REGISTERED_RUNTIME_PACKAGES), None)
                    if registered:
                        advisories.append('tex_runtime_dependency_unavailable: ' + label)
                        found = True
                if not found:
                    if command in ('usepackage', 'RequirePackage', 'documentclass', 'documentstyle', 'LoadClass', 'bibliographystyle'):
                        advisories.append('unresolved_runtime_or_author_dependency: ' + label)
                    else:
                        missing.append(label)
    return sorted(set(missing))


def source_classification(missing, advisories):
    runtime = sorted(set(x for x in advisories if x.startswith('tex_runtime_dependency_unavailable:')))
    unresolved = sorted(set(x for x in advisories if x.startswith(('unresolved_dynamic_dependency:', 'unresolved_runtime_or_author_dependency:'))))
    return {'status': 'missing_materials' if missing else 'raw_acquired_needs_resolution' if unresolved else 'complete',
            'missing_materials': sorted(set(missing)),
            'dependency_classification': {'missing_local_assets': sorted(set(missing)), 'runtime_unavailable': runtime, 'unresolved': unresolved},
            'runtime_compile_readiness': 'runtime_dependency_unavailable' if runtime else 'not_checked'}

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag in ('a', 'img'):
            values = dict(attrs)
            link = values.get('href' if tag == 'a' else 'src')
            if link:
                self.links.append((link, tag))

def require_disk_capacity(paths,min_free_bytes,pending_bytes=0):
    for name in dict.fromkeys(map(str,paths)):
        path=Path(name)
        try:
            if not path.exists() or shutil.disk_usage(path).free-pending_bytes<min_free_bytes:
                raise Held('disk_space_held: '+name)
        except OSError as error:raise Held('disk_capacity_unreadable: '+name) from error


GIB = 1024 ** 3
STORAGE_WORKING_RESERVE = 50 * GIB
STORAGE_EMERGENCY_RESERVE = 20 * GIB
STORAGE_WARNING_FLOOR = 100 * GIB
UNKNOWN_INPUT_BYTES = GIB
UNKNOWN_ASSET_BYTES = GIB
UNKNOWN_GIT_BYTES = 256 * 1024 ** 2
UNKNOWN_RAW_BYTES = 2 * 64 * 1024 ** 2


def capacity_inputs(project_root):
    """Read sizes from the current authority; do not materialize the database."""
    root = Path(project_root)
    queue = root / 'repo/handoff/yupeng/PRODUCTION_QUEUE.json'
    if not queue.exists():
        return {'database_bytes': GIB, 'metadata_bytes': 256 * 1024 ** 2,
                'basis': 'conservative_bootstrap_no_public_queue'}
    try:
        base = json.loads(queue.read_text())['base']
        database = Path(base['master_database'])
        package = Path(base['package'])
        if not database.is_file():
            raise Held('disk_capacity_baseline_missing: ' + str(database))
        names = ('manifest.json', 'work-registry.jsonl', 'prepared-database.json')
        metadata = sum((package / name).stat().st_size for name in names
                       if (package / name).is_file())
        if not metadata:
            metadata = 256 * 1024 ** 2
        return {'database_bytes': database.stat().st_size,
                'metadata_bytes': metadata, 'basis': 'current_public_queue',
                'database': str(database), 'package': str(package)}
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise Held('disk_capacity_baseline_unreadable: ' + str(queue)) from error


def storage_capacity_budget(database_bytes, metadata_bytes, asset_bytes=0,
                            git_bytes=0, input_bytes=0, raw_bytes=0, *, stage='prepare'):
    """Approved full budget; later stages reserve only not-yet-created copies."""
    sizes = dict(database_bytes=database_bytes, metadata_bytes=metadata_bytes,
                 asset_bytes=asset_bytes, git_bytes=git_bytes,
                 input_bytes=input_bytes, raw_bytes=raw_bytes)
    if any(type(value) is not int or value < 0 for value in sizes.values()):
        raise ValueError('storage sizes must be nonnegative integer bytes')
    remaining = {'material': 3, 'download': 3, 'prepare': 3, 'candidate': 2, 'public': 1}
    if stage not in remaining:
        raise ValueError('unknown allocation stage: ' + str(stage))
    copies = remaining[stage]
    total = ((copies + 1) * database_bytes + copies * metadata_bytes
             + copies * asset_bytes + git_bytes + input_bytes + raw_bytes)
    pending = (3 * total + 1) // 2
    return {'policy': 'bounded-publication-capacity-v1-20261115', 'stage': stage,
            'inputs': sizes, 'remaining_SQL_copies': copies,
            'SQLite_temporary_copy_budget': 1, 'safety_numerator': 3,
            'safety_denominator': 2, 'pending_bytes': pending,
            'working_reserve_bytes': STORAGE_WORKING_RESERVE,
            'emergency_reserve_bytes': STORAGE_EMERGENCY_RESERVE,
            'warning_free_bytes': max(STORAGE_WARNING_FLOOR,
                                      2 * pending + STORAGE_WORKING_RESERVE)}


class CapacityMaintenanceRequired(Held):
    """Capacity is a resumable operational hold, never a material judgement."""
    def __init__(self, report):
        self.capacity_report = report
        super().__init__('capacity_maintenance_required: ' + report.get('state', 'capacity_unknown_hold'))


def project_maintenance_program(project_root):
    path = Path(project_root) / '.work/whole-work-production-20261114/PROGRAM.json'
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as error:
        raise Held('disk_capacity_policy_unreadable: ' + str(path)) from error


def capacity_maintenance_decision(report, *, previous_state=None):
    """Pure dynamic entry/exit decision for the original project only."""
    if report.get('enforce_project_reserve') is False:
        return dict(state='normal', project_maintenance=False)
    pending = report.get('pending_bytes')
    rows = report.get('filesystems', [])
    if (type(pending) is not int or pending < 0 or len(rows) < 2
            or len({row.get('path') for row in rows}) < 2
            or any(type(row.get('free_bytes')) is not int or row['free_bytes'] < 0 for row in rows)):
        return dict(state='capacity_unknown_hold', reason='both actual filesystem free values are required')
    warning = max(100 * 1024**3, 2 * pending + STORAGE_WORKING_RESERVE)
    resume = warning + 20 * 1024**3
    held = previous_state not in (None, 'normal')
    threshold = resume if held else warning
    limited = [row['path'] for row in rows if row['free_bytes'] < max(threshold, pending + STORAGE_WORKING_RESERVE)]
    state = 'maintenance_requested' if limited else 'normal'
    host = [row for row in rows if row.get('role') == 'host']
    guest = [row for row in rows if row.get('role') == 'project']
    if held and host and guest and guest[0]['free_bytes'] >= resume and host[0]['free_bytes'] < resume:
        state = 'host_reclaim_pending'
    return dict(state=state, warning_free_bytes=warning, resume_free_bytes=resume,
                required_allocation_bytes=pending + STORAGE_WORKING_RESERVE,
                limited_filesystems=limited, pending_bytes=pending,
                below_emergency=any(row['free_bytes'] < STORAGE_EMERGENCY_RESERVE for row in rows))


def require_storage_capacity(paths, budget, *, min_free_bytes=STORAGE_WORKING_RESERVE,
                             enforce_project_reserve=True, maintenance_enabled=False, host_path=None, maintenance_previous_state=None):
    paths = list(dict.fromkeys(map(Path, paths)))
    reserve = max(STORAGE_WORKING_RESERVE, min_free_bytes) if enforce_project_reserve else max(0, min_free_bytes)
    scope = 'project_production' if enforce_project_reserve else 'portable_consumer'
    warning = budget['warning_free_bytes'] if enforce_project_reserve else budget['pending_bytes']
    try:
        require_disk_capacity(paths, reserve, budget['pending_bytes'])
    except Held as error:
        held = Held(str(error) + '; pending_bytes=' + str(budget['pending_bytes'])
                    + '; working_reserve_bytes=' + str(reserve))
        held.capacity_budget = budget
        rows = []
        for path in paths:
            try:free = shutil.disk_usage(path).free
            except OSError:free = None
            rows.append(dict(path=str(path), free_bytes=free,
                             role='host' if path == Path(host_path or paths[-1]) else 'project'))
        held.capacity_report = dict(budget, filesystems=rows, enforce_project_reserve=enforce_project_reserve,
                                    state='HELD', reason=str(error))
        if maintenance_enabled and enforce_project_reserve:
            decision = capacity_maintenance_decision(held.capacity_report, previous_state=maintenance_previous_state)
            failure = dict(held.capacity_report, maintenance_state=decision['state'])
            if decision['state'] == 'capacity_unknown_hold':failure['state'] = decision['state']
            raise CapacityMaintenanceRequired(failure) from error
        raise held from error
    filesystems = []
    for name in paths:
        free = shutil.disk_usage(name).free
        filesystems.append({'path': str(name), 'free_bytes': free,
                            'role': 'host' if name == Path(host_path or paths[-1]) else 'project',
                            'warning': free < warning,
                            'below_emergency': enforce_project_reserve and free < STORAGE_EMERGENCY_RESERVE})
    report = dict(budget, working_reserve_bytes=reserve, filesystems=filesystems,
                reserve_scope=scope, enforce_project_reserve=enforce_project_reserve,
                emergency_reserve_bytes=STORAGE_EMERGENCY_RESERVE if enforce_project_reserve else 0,
                warning_free_bytes=warning,
                state='SPACE_WARNING' if any(row['warning'] for row in filesystems)
                else 'SPACE_AVAILABLE')
    if maintenance_enabled and enforce_project_reserve:
        decision = capacity_maintenance_decision(report, previous_state=maintenance_previous_state)
        if decision['state'] != 'normal':
            raise CapacityMaintenanceRequired(dict(report, **decision))
    return report


class Acquirer:
    def __init__(self, cache, workers=4, min_free_gib=20):
        self.cache = Path(cache)
        self.workers = max(1, min(4, workers))
        self.min_free = min_free_gib * 1024**3
        self.lock = threading.Lock()
        self.hosts = {}
        self.work_hosts = {}
        self.last_started = {}
        self._capacity_local = threading.local()
        holds = self.cache / 'ACCESS_HOLDS.json'
        self.held_until = json.loads(holds.read_text(encoding='utf-8')) if holds.is_file() else {}

    @property
    def last_capacity_report(self):
        return getattr(self._capacity_local, 'report', None)

    @last_capacity_report.setter
    def last_capacity_report(self, value):
        self._capacity_local.report = value

    def space(self, pending_bytes=0):
        project_root=Path(__file__).resolve().parents[3]
        paths=[self.cache,project_root,Path('/mnt/e')]
        programme = project_maintenance_program(project_root)
        try:inputs = capacity_inputs(project_root)
        except Held as error:
            self.last_capacity_report = dict(state='capacity_unknown_hold', reason=str(error), filesystems=[])
            if programme.get('storage_maintenance_policy', {}).get('enabled') is True:
                raise CapacityMaintenanceRequired(self.last_capacity_report) from error
            raise
        # The whole download pool shares this reservation, including unknown
        # Content-Length and archive expansion before any larger known size.
        budget = storage_capacity_budget(inputs['database_bytes'], inputs['metadata_bytes'],
            UNKNOWN_ASSET_BYTES, UNKNOWN_GIT_BYTES,
            max(UNKNOWN_INPUT_BYTES, pending_bytes) * self.workers,
            UNKNOWN_RAW_BYTES, stage='download')
        budget['baseline_basis'] = inputs['basis']
        budget['download_workers_reserved'] = self.workers
        self.last_capacity_report = budget
        try:
            self.last_capacity_report = require_storage_capacity(paths, budget,
                min_free_bytes=max(self.min_free, STORAGE_WORKING_RESERVE),
                maintenance_enabled=programme.get('storage_maintenance_policy', {}).get('enabled') is True,
                maintenance_previous_state=programme.get('storage_maintenance', {}).get('state'))
        except Held as error:
            self.last_capacity_report = getattr(error, 'capacity_report', dict(budget, state='HELD', reason=str(error)))
            raise
        return self.last_capacity_report


    @contextmanager
    def host(self, url):
        hostname = host_family(url)
        if urlsplit(url).scheme not in ('http', 'https') or not hostname:
            raise ValueError('only explicit HTTP(S) source URLs are supported')
        with self.lock:
            semaphore = self.hosts.setdefault(hostname, threading.Semaphore(1))
        with semaphore:
            if self.held_until.get(hostname, 0) > time.time():
                raise Held('access_held: host Retry-After active')
            yield hostname

    def start_request(self, hostname):
        if hostname == 'arxiv.org':
            delay = self.last_started.get(hostname, -3) + 3 - time.monotonic()
            if delay > 0:time.sleep(delay)
            self.last_started[hostname] = time.monotonic()

    def save_hold(self, hostname, until):
        with self.lock:
            self.held_until[hostname] = until
            self.cache.mkdir(parents=True, exist_ok=True)
            temporary = self.cache / 'ACCESS_HOLDS.tmp'
            temporary.write_text(json.dumps(self.held_until, indent=2), encoding='utf-8')
            temporary.replace(self.cache / 'ACCESS_HOLDS.json')

    def fetch(self, url, target):
        for hop in range(6):
            destination = self._fetch_one(url, target)
            if destination is None:
                return url
            url = destination
        raise ValueError('source exceeded 5 redirects')

    def _fetch_one(self, url, target):
        with self.host(url) as hostname:
            for attempt in range(2):
                self.space()
                self.start_request(hostname)
                try:
                    with build_opener(NoRedirect()).open(Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; AuthorWorksAcquisition/1.1)'}), timeout=45) as response:
                        declared = response.headers.get('Content-Length')
                        try:
                            remaining = max(0, int(declared)) if declared is not None else UNKNOWN_INPUT_BYTES
                        except (TypeError, ValueError):
                            remaining = UNKNOWN_INPUT_BYTES
                        self.space(remaining)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with target.open('wb') as output:
                            while True:
                                self.space(remaining)
                                block = response.read(1024 * 1024)
                                if not block:
                                    break
                                self.space(max(remaining, len(block)))
                                output.write(block)
                                remaining = max(0, remaining - len(block))
                    return
                except HTTPError as error:
                    error.close()
                    if error.code in (301, 302, 303, 307, 308):
                        location = error.headers.get('Location')
                        if not location:
                            raise ValueError('redirect without Location')
                        return urljoin(url, location)
                    if error.code in (401, 403, 429) or error.headers.get('Retry-After'):
                        retry = error.headers.get('Retry-After', '60')
                        try:
                            until = time.time() + max(0, float(retry))
                        except ValueError:
                            try:
                                until = parsedate_to_datetime(retry).timestamp()
                            except (ValueError, TypeError):
                                until = time.time() + 60
                        self.save_hold(hostname, max(time.time()+1, until))
                        raise Held('access_held: HTTP %s Retry-After=%s' % (error.code, retry))
                    if error.code < 500 or attempt:
                        raise
                except (URLError, OSError):
                    if attempt:
                        raise

    def acquire(self, row):
        self.last_capacity_report = None
        if row.get('acquisition_state', 'ready') != 'ready':
            return dict(row, status=row['acquisition_state'], qualified_items=0)
        if row['kind'] == 'arxiv' and not re.search(r'v\d+$', row['source_version']):
            return dict(row, status='pending_version', qualified_items=0)
        hostname = host_family(row['source_url'])
        with self.lock:
            semaphore = self.work_hosts.setdefault(hostname, threading.Semaphore(1))
        with semaphore:
            return self._acquire(row)

    def obtain(self, row, url, target, state):
        for asset in row.get('cached_assets', []):
            cached = Path(asset['path'])
            if url in (asset.get('url'), asset.get('final_url')) and cached.is_file():
                if asset.get('source_version') not in (None, row['source_version']):continue
                remaining = cached.stat().st_size
                self.space(remaining)
                target.parent.mkdir(parents=True, exist_ok=True)
                with cached.open('rb') as source, target.open('wb') as output:
                    checked_copy(source, output, self.space, remaining_bytes=remaining)
                state.setdefault('reused_assets', []).append({'url':url, 'path':str(cached)})
                return asset.get('final_url') or url
        final_url = self.fetch(url, target)
        state.setdefault('downloaded_urls', []).append(final_url)
        return final_url


    def _acquire(self, row):
        root = self.cache / work_directory(row['work_key'])
        record = root / 'SOURCE.json'
        old = json.loads(record.read_text(encoding='utf-8')) if record.exists() else None
        if old and old['work_key'] != row['work_key']:
            return dict(row, status='error', reason='work directory collision', qualified_items=0)
        if old and old.get('source_version') == row['source_version'] and old.get('source_url') == row['source_url'] and old.get('assets', []) == row.get('assets', []) and old.get('status') == 'complete' and old.get('files') and all((root / old.get('source_dir', 'source') / relative_path(name)).is_file() for name in old['files']):
            return dict(old, reused=True)
        if old and (old.get('source_version') != row['source_version'] or old.get('source_url') != row['source_url'] or old.get('assets', []) != row.get('assets', [])):
            return dict(row, status='version_conflict', reason='preserve existing version; choose a separate versioned work_key', qualified_items=0)
        root.mkdir(parents=True, exist_ok=True)
        attempt = int(old.get('attempt', 1)) + 1 if old else 1
        source_dir = 'source' if attempt == 1 else 'source-attempt-%04d' % attempt
        while (root / source_dir).exists():
            attempt += 1
            source_dir = 'source-attempt-%04d' % attempt
        state = dict(row, status='acquiring', qualified_items=0, attempt=attempt, source_dir=source_dir)
        record.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        source = root / source_dir
        source.mkdir(exist_ok=True)
        try:
            advisories = []
            urls = [row['source_url']] + row.get('assets', [])
            landing_url = row['source_url'] if row['kind'] == 'landing' else row.get('landing_url')
            if landing_url:
                landing = root / ('landing-attempt-%04d.html' % attempt)
                actual_landing = self.obtain(row, landing_url, landing, state)
                if row['kind'] == 'landing':urls = list(row.get('assets', []))
                urls.extend(visible_attachments(row, actual_landing, landing.read_text(encoding='utf-8', errors='replace')))
            if not urls:
                raise Held('missing_materials: no explicit source attachments')
            names = {}
            for url in dict.fromkeys(urls):
                path = unquote(urlsplit(url).path)
                name = Path(path).name or 'source.archive'
                base_path = urlsplit(row['source_url']).path.rsplit('/', 1)[0] + '/'
                relative_name = path[len(base_path):] if path.startswith(base_path) else name
                publisher_path = re.search(r'/article/10\.5802/[a-z]+\.\d+/file/src/[^/]+/(.+)$', path)
                if publisher_path:relative_name = publisher_path.group(1)
                relative = relative_path(row.get('asset_paths', {}).get(url, relative_name or name))
                if str(relative) in names and names[str(relative)] != url:
                    raise ValueError('attachment filename collision: ' + name)
                names[str(relative)] = url
                target = source / relative
                self.obtain(row, url, target, state)
                unpack_native_source(target, row['kind'] if url == row['source_url'] else 'tex', self.space, advisories,
                                     attachment=(url != row['source_url']))
            missing = missing_materials(source, advisories)
            body_files = [path for path in source.rglob('*') if path.is_file() and path.suffix.lower() in ('.tex', '.lean')]
            state.update(source_classification(missing, advisories), advisories=sorted(set(advisories)))
            if not body_files:
                state['status'] = 'acquired_raw_needs_body_identification'
        except Held as error:
            state.update(status=str(error).split(':')[0], reason=str(error))
        except Exception as error:
            state.update(status='error', reason=str(error))
        files = [path for path in source.rglob('*') if path.is_file()]
        state.update(source_files=len(files), source_bytes=sum(path.stat().st_size for path in files), files=sorted(str(path.relative_to(source)).replace('\\', '/') for path in files))
        if self.last_capacity_report is not None:
            state['storage_capacity'] = self.last_capacity_report
        record.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        (root / ('SOURCE-attempt-%04d.json' % attempt)).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        return state

    def run(self, rows):
        self.cache.mkdir(parents=True, exist_ok=True)
        keys = [work_directory(row['work_key']) for row in rows]
        if len(keys) != len(set(key.casefold() for key in keys)):
            raise ValueError('duplicate or colliding work directories in queue')
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            results = list(executor.map(self.acquire, rows))
        progress = {'works':len(results), 'complete':sum(row['status']=='complete' for row in results), 'source_files':sum(row.get('source_files',0) for row in results), 'source_bytes':sum(row.get('source_bytes',0) for row in results), 'qualified_items':0, 'results':results}
        (self.cache / 'progress.json').write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')
        return progress

RECLASSIFICATION_METHOD = 'retained-source-dependencies-v1'
CLASSIFICATION_FIELDS = ('status', 'missing_materials', 'advisories', 'classification_basis', 'dependency_classification', 'runtime_compile_readiness')
CLASSIFICATION_ADVISORIES = ('tex_runtime_dependency:', 'tex_runtime_dependency_unavailable:',
                            'retained_bibliography_output:', 'unresolved_dynamic_dependency:', 'unresolved_runtime_or_author_dependency:')


def source_stat(path):
    value = path.stat()
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


def json_candidate(path, value):
    """Durable same-directory candidate; failed CAS candidates remain evidence."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n', dir=path.parent,
                                     prefix='.' + path.name + '.reclassify-', suffix='.tmp', delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
        return Path(stream.name)


def reclassify_sources(rows, cache, *, apply=False, report_path=None, work_keys=None, limit=6, min_age_seconds=300):
    """Reclassify retained terminal sources only; never acquire or edit author files.

    Apply callers serialize maintenance with the controller. A unique original
    queue, terminal-age guard and final stat/state CAS avoid observed live writes.
    Reports retain pre-change classification fields before each SOURCE rename.
    """
    cache = Path(cache).resolve()
    if limit < 1 or min_age_seconds < 0:
        raise ValueError('positive limit and nonnegative minimum age required')
    report_path = Path(report_path).resolve() if report_path else None
    if apply and report_path is None:
        raise ValueError('apply requires a durable classification report')
    if report_path and report_path.is_relative_to(cache):
        raise ValueError('classification report must be outside the source cache')
    journal = json.loads(report_path.read_text(encoding='utf-8')) if report_path and report_path.exists() else {
        'schema_version': 1, 'kind': 'source_metadata_reclassification', 'cache': str(cache), 'runs': []}
    if journal.get('kind') != 'source_metadata_reclassification' or journal.get('cache') != str(cache):
        raise ValueError('existing classification report belongs to another operation/cache')
    run = {'apply': apply, 'started_at': time.time(), 'qualified_increment': 0, 'results': []}
    journal['runs'].append(run)
    counts = Counter(row['work_key'] for row in rows)
    directories = Counter(work_directory(row['work_key']).casefold() for row in rows)
    selected = set(work_keys) if work_keys else None
    seen = set()

    def persist():
        run['counts'] = dict(Counter(item['decision'] for item in run['results']))
        run['actual_SOURCE_updates'] = run['counts'].get('applied', 0)
        if report_path:
            os.replace(json_candidate(report_path, journal), report_path)

    for queued in rows:
        key = queued['work_key']
        if key in seen or selected is not None and key not in selected:
            continue
        if len(run['results']) >= limit:
            break
        seen.add(key)
        item = {'work_key': key, 'qualified_increment': 0}
        run['results'].append(item)
        if counts[key] != 1 or directories[work_directory(key).casefold()] != 1:
            item['decision'] = 'skipped_duplicate_queue_key'; persist(); continue
        record = cache / work_directory(key) / 'SOURCE.json'
        item['source_record'] = str(record)
        try:
            before_stat = source_stat(record)
            old = json.loads(record.read_text(encoding='utf-8'))
            if source_stat(record) != before_stat:
                item['decision'] = 'skipped_changed_during_read'; persist(); continue
            if old.get('status') != 'missing_materials':
                item['decision'] = 'skipped_status'; persist(); continue
            if time.time() - record.stat().st_mtime < min_age_seconds:
                item['decision'] = 'skipped_fresh'; persist(); continue
            if any(old.get(field) != queued.get(field) for field in ('work_key', 'source_url', 'source_version')):
                item['decision'] = 'skipped_identity_conflict'; persist(); continue
            if not isinstance(old.get('source_dir'), str) or not old['source_dir']:
                item['decision'] = 'skipped_source_dir_missing'; persist(); continue
            source = (record.parent / relative_path(old['source_dir'])).resolve()
            if not source.is_relative_to(record.parent.resolve()) or not source.is_dir():
                item['decision'] = 'skipped_source_dir_missing'; persist(); continue
            derived = []
            missing = missing_materials(source, derived)
            if not any(path.is_file() and path.suffix.lower() in ('.tex', '.lean') for path in source.rglob('*')):
                missing = sorted(set(missing) | {'source_body: no retained TeX or Lean body'})
            advisories = sorted(set(value for value in old.get('advisories', []) if not value.startswith(CLASSIFICATION_ADVISORIES)) | set(derived))
            after = {**source_classification(missing, advisories), 'advisories': advisories,
                     'classification_basis': {'method': RECLASSIFICATION_METHOD, 'scope': 'retained files only; exact runtime registry and matching nonempty bbl; no downloads', 'qualified_increment': 0}}
            item.update(source_dir=old['source_dir'], source_version=old.get('source_version'), attempt=old.get('attempt'),
                        stat_before=list(before_stat), before={field: old.get(field) for field in CLASSIFICATION_FIELDS},
                        originally_missing_fields=[field for field in CLASSIFICATION_FIELDS if field not in old], after=after)
            if all(old.get(field) == value for field, value in after.items()):
                item['decision'] = 'unchanged'; persist(); continue
            item['decision'] = 'prepared' if apply else 'preview_change'
            persist()
            if not apply:
                continue
            updated = dict(old, **after)
            candidate = json_candidate(record, updated)
            item['candidate_path'] = str(candidate)
            # Check again immediately before atomic rename, including status,
            # every metadata field and a second stat after the final read.
            latest_stat = source_stat(record)
            latest = json.loads(record.read_text(encoding='utf-8'))
            if latest_stat != before_stat or source_stat(record) != before_stat or latest != old or latest.get('status') != 'missing_materials':
                item['decision'] = 'skipped_concurrent_change'; persist(); continue
            os.replace(candidate, record)
            item['decision'] = 'applied'
            persist()
        except (OSError, ValueError, json.JSONDecodeError) as error:
            if item.get('decision') == 'applied':
                # The prior durable prepared receipt survives a report-write
                # failure; never relabel a successful SOURCE rename as a skip.
                raise
            item.update(decision='skipped_error', error=str(error)); persist()
    persist()
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queue', required=True, type=Path)
    parser.add_argument('--cache', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--min-free-gib', type=float, default=20)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--reclassify', action='store_true', help='Preview existing terminal missing_materials; no downloads')
    parser.add_argument('--apply', action='store_true', help='Apply reclassification only under owner serialization')
    parser.add_argument('--classification-report', type=Path)
    parser.add_argument('--work-key', action='append', help='Limit reclassification to explicit existing queue work keys')
    parser.add_argument('--limit', type=int, default=6)
    parser.add_argument('--min-source-age-seconds', type=float, default=300)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.queue.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    for row in rows:
        for key in ('work_key','title','authors','source_url','source_version','license','kind'):
            if key not in row:
                parser.error('missing queue field: ' + key)
        if row['kind'] not in ('archive','tex','landing','arxiv'):
            parser.error('unsupported kind')
    if args.reclassify:
        if args.run:
            parser.error('reclassification cannot run acquisition')
        result = reclassify_sources(rows, args.cache, apply=args.apply, report_path=args.classification_report,
                                    work_keys=args.work_key, limit=args.limit, min_age_seconds=args.min_source_age_seconds)
    else:
        if args.apply:
            parser.error('--apply requires --reclassify')
        result = Acquirer(args.cache, args.workers, args.min_free_gib).run(rows) if args.run else {'planned_works': rows, 'cache':str(args.cache), 'qualified_items':0, 'run':False}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
