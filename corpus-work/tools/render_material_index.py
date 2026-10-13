"""Generate a material reading view without changing corpus IDs or admission state."""
import argparse
import html
import json
import re
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit

POLICY = 'reviewed-revision-v2'


def natural_key(identifier):
    # Numeric IDs precede named IDs; original spelling is never rewritten.
    if identifier.isascii() and identifier.isdecimal():
        return (0, int(identifier), identifier)
    return (1, tuple((0, int(p)) if p.isdecimal() else (1, p.casefold())
                     for p in re.split(r'(\d+)', identifier) if p), identifier)


def cell(value):
    text = ' '.join(str(value or '').split())
    return html.escape(text, quote=False).replace('\\', '\\\\').replace('|', '&#124;').replace('[', '\\[').replace(']', '\\]')


def package_link(label, value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('invalid package-relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or ':' in value:
        raise ValueError('unsafe package-relative path')
    return '['+label+']('+quote(value, safe='/._-')+')'


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
    lines = ['# 全量材料阅读索引', '',
             '来源快照（生成者指定）：`'+snapshot+'`。材料共 **'+str(len(rows))+'** 条：legacy **'+str(len(rows)-prepared)+'**，prepared **'+str(prepared)+'**。', '',
             '展示序号仅为此快照的阅读顺序；稳定 problem_id、来源、许可和审阅身份不变。材料状态、历史 H 标签、prepared 或 status 字段均不自动证明现行科学资格，序号也不是新增/交付计数。', '',
             '本视图由 `corpus-work/tools/render_material_index.py` 从 manifest 全部材料重新生成，不供五列 INDEX 门禁解析器使用。旧交付 [INDEX](INDEX.md) 与历史 [CORPUS_INDEX/catalog](CORPUS_INDEX.md) 保持各自覆盖范围。', '',
             '从仓库根重新生成（先取得匹配来源快照的 manifest）：', '',
             '```sh', 'python3 corpus-work/tools/render_material_index.py --package editable-corpus --snapshot '+snapshot,
             '# 只检查过期/缺失/多余行，不覆盖文件',
             'python3 corpus-work/tools/render_material_index.py --package editable-corpus --snapshot '+snapshot+' --check', '```', '',
             '| 展示序号 | 稳定 problem_id | 标题 | 既有难度标签 | 原材料/审阅状态（非资格结论） | TeX | 来源及许可/审阅 |',
             '|---|---|---|---|---|---|---|']
    for ordinal,row in enumerate(sorted(rows,key=lambda r:natural_key(r['problem_id'])),1):
        url = row.get('source_url','')
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
        lines.append('| '+' | '.join(columns)+' |')
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True)
    parser.add_argument('--snapshot',required=True,help='40-character source commit label; use its matching manifest')
    parser.add_argument('--check',action='store_true',help='fail on stale/missing view without writing')
    args = parser.parse_args()
    try:
        if not re.fullmatch(r'[0-9a-f]{40}',args.snapshot):
            raise ValueError('snapshot must be a 40-character commit label')
        manifest = json.loads((args.package/'manifest.json').read_text(encoding='utf8'))
        data = render(manifest,args.snapshot).encode('utf8')
        output = args.package/'MATERIAL_INDEX.md'
        if output.is_symlink():
            raise ValueError('refusing symlink output')
        if args.check:
            # Git may convert LF to CRLF on checkout; compare view text only.
            if not output.is_file() or output.read_text(encoding='utf8') != data.decode('utf8'):
                raise ValueError('material reading view is stale or missing')
        else:
            output.write_bytes(data)
        print(('Checked' if args.check else 'Generated')+' '+str(len(manifest['items']))+' material rows')
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(1,str(exc)+'\n')


if __name__ == '__main__':
    main()
