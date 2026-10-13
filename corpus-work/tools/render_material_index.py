"""Generate a material reading view without changing corpus IDs or admission state."""
import argparse
import html
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit

POLICY = 'reviewed-revision-v2'
PAGE_SIZE = 200


def natural_key(identifier):
    # Numeric IDs precede named IDs; original spelling is never rewritten.
    if identifier.isascii() and identifier.isdecimal():
        return (0, int(identifier), identifier)
    return (1, tuple((0, int(p)) if p.isdecimal() else (1, p.casefold())
                     for p in re.split(r'(\d+)', identifier) if p), identifier)


def cell(value):
    text = ' '.join(str(value or '').split())
    text = html.escape(text, quote=False).replace('|', '&#124;')
    return re.sub(r'([\\*_`\[\]$])', r'\\\1', text)


def package_link(label, value, prefix='../'):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('invalid package-relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or ':' in value:
        raise ValueError('unsafe package-relative path')
    return '['+label+']('+quote(prefix+value, safe='/._-')+')'


def state(row):
    fields = ['prepared' if row.get('policy') == POLICY else 'legacy']
    for key in ('status','review_state','preparation_basis','review_protocol','qualification_set_id'):
        if row.get(key):
            fields.append(key+'='+str(row[key]))
    return cell('; '.join(fields))


def render(manifest, snapshot):
    rows = manifest['items']
    if not isinstance(rows, list):
        raise ValueError('manifest items must be a list')
    identifiers = set(); numbers = set(); paths = set()
    for row in rows:
        ident = row.get('problem_id')
        if not isinstance(ident,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}',ident):
            raise ValueError('invalid stable ID')
        if ident in identifiers:
            raise ValueError('duplicate stable ID: '+ident)
        identifiers.add(ident)
        if ident.isascii() and ident.isdecimal():
            number = int(ident)
            if number in numbers:
                raise ValueError('numeric alias: '+ident)
            numbers.add(number)
        if row['item_path'] in paths:
            raise ValueError('duplicate item path: '+row['item_path'])
        paths.add(row['item_path'])
    prepared = sum(r.get('policy') == POLICY for r in rows)
    intro = ['# 全量材料阅读索引', '',
             '来源快照：`'+snapshot+'`（已核对 manifest 内容，仅允许 Git checkout 换行差异）。材料共 **'+str(len(rows))+'** 条：legacy **'+str(len(rows)-prepared)+'**，prepared **'+str(prepared)+'**。', '',
             '展示序号仅为此快照的阅读顺序；稳定 problem_id、来源、许可和审阅身份不变。材料状态、历史 H 标签、prepared 或 status 字段均不自动证明现行科学资格，序号也不是新增/交付计数。', '',
             '本视图由 `corpus-work/tools/render_material_index.py` 从 manifest 全部材料重新生成，不供五列 INDEX 门禁解析器使用。旧交付 [INDEX](INDEX.md) 与历史 [CORPUS_INDEX/catalog](CORPUS_INDEX.md) 保持各自覆盖范围。', '',
             '从仓库根重新生成（先取得匹配来源快照的 manifest）：', '',
             '```sh', 'python3 corpus-work/tools/render_material_index.py --package editable-corpus --snapshot '+snapshot,
             '# 只检查过期/缺失/多余行，不覆盖文件',
             'python3 corpus-work/tools/render_material_index.py --package editable-corpus --snapshot '+snapshot+' --check', '```', '',
             '每页最多 200 条，各页序号延续全局顺序；每条仅出现在一页。', '',
             '| 页面 | 全局展示序号 | 稳定 ID 范围 |', '|---|---|---|']
    output = {}; page_lines = []
    ordered = sorted(rows,key=lambda r:natural_key(r['problem_id']))
    page_count = (len(rows)+PAGE_SIZE-1)//PAGE_SIZE
    for ordinal,row in enumerate(ordered,1):
        url = row.get('source_url','')
        primary = row.get('primary')
        if isinstance(primary,dict):
            url = primary.get('tag_url') or url
        if url and urlsplit(url).scheme not in ('http','https'):
            raise ValueError('unsafe source URL')
        evidence = ['[来源]('+quote(url,safe=':/?#=&%+-._~')+')'] if url else []
        if row.get('license_path'):
            evidence.append(package_link('许可',row['license_path']))
        if row.get('compile_receipt'):
            evidence.append(package_link('既有回执',row['compile_receipt']))
        if row.get('prepared_job'):
            evidence.append(package_link('审阅/任务',row['prepared_job']+'/'))
        else:
            evidence.append(package_link('元数据','sources/'+row['problem_id']+'/provenance.json'))
        columns = [str(ordinal),row['problem_id'],cell(row.get('title')),cell(row.get('difficulty_level')),
                   state(row),package_link('TeX',row['item_path']),' '.join(evidence)]
        page_lines.append('| '+' | '.join(columns)+' |')
        if ordinal % PAGE_SIZE == 0 or ordinal == len(rows):
            number = (ordinal-1)//PAGE_SIZE+1
            start = (number-1)*PAGE_SIZE+1
            filename = 'page-'+str(number).zfill(3)+'.md'
            intro.append('| [第 '+str(number)+' 页](material-index/'+filename+') | '+str(start)+'–'+str(ordinal)+' | '+ordered[start-1]['problem_id']+'–'+row['problem_id']+' |')
            navigation = ['[总入口](../MATERIAL_INDEX.md)']
            if number > 1:
                navigation.append('[上一页](page-'+str(number-1).zfill(3)+'.md)')
            if number < page_count:
                navigation.append('[下一页](page-'+str(number+1).zfill(3)+'.md)')
            page = ['# 材料阅读：第 '+str(number)+' / '+str(page_count)+' 页', '',
                    ' · '.join(navigation), '', '来源快照：`'+snapshot+'`。全局展示序号 '+str(start)+'–'+str(ordinal)+'；序号/原状态/难度标签不是资格结论。', '',
                    '| 展示序号 | 稳定 problem_id | 标题 | 既有难度标签 | 原材料/审阅状态（非资格结论） | TeX | 来源及许可/审阅 |',
                    '|---|---|---|---|---|---|---|', *page_lines, '', ' · '.join(navigation), '']
            output['material-index/'+filename] = '\n'.join(page)
            page_lines = []
    output['MATERIAL_INDEX.md'] = '\n'.join(intro)+'\n'
    return output


def strict_object(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: '+key)
        result[key] = value
    return result


def match_snapshot(package, snapshot, raw):
    try:
        repository = Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=package,text=True,stderr=subprocess.DEVNULL).strip()).resolve()
        relative = (package/'manifest.json').resolve().relative_to(repository).as_posix()
        original = subprocess.check_output(['git','show',snapshot+':'+relative],cwd=repository,stderr=subprocess.DEVNULL)
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:
        raise ValueError('snapshot manifest is unavailable') from exc
    if raw.replace(b'\r\n',b'\n') != original.replace(b'\r\n',b'\n'):
        raise ValueError('snapshot manifest does not match working input')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--snapshot',required=True,help='40-character source commit label; use its matching manifest')
    parser.add_argument('--check',action='store_true',help='fail on stale/missing view without writing')
    args = parser.parse_args()
    try:
        if not re.fullmatch(r'[0-9a-f]{40}',args.snapshot):
            raise ValueError('snapshot must be a 40-character commit label')
        raw = (args.package/'manifest.json').read_bytes()
        manifest = json.loads(raw.decode('utf8'),object_pairs_hook=strict_object)
        match_snapshot(args.package.resolve(),args.snapshot,raw)
        views = render(manifest,args.snapshot)
        folder = args.package/'material-index'
        if folder.is_symlink():
            raise ValueError('refusing symlink output')
        expected = {args.package/name for name in views}
        extras = set(folder.glob('page-*.md'))-expected
        if extras:
            raise ValueError('unexpected extra reading pages; preserve and review them')
        if any(p.is_symlink() for p in expected):
            raise ValueError('refusing symlink output')
        if args.check:
            # Git may convert LF to CRLF on checkout; compare view text only.
            for name,text in views.items():
                output = args.package/name
                if not output.is_file() or output.read_text(encoding='utf8') != text:
                    raise ValueError('material reading view is stale or missing: '+name)
        else:
            folder.mkdir(exist_ok=True)
            # Publish the small navigation file only after all pages are written.
            for name,text in views.items():
                (args.package/name).write_bytes(text.encode('utf8'))
        print(('Checked' if args.check else 'Generated')+' '+str(len(manifest['items']))+' material rows')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(1,str(exc)+'\n')


if __name__ == '__main__':
    main()
