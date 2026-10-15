#!/usr/bin/env python3
"""Add source-path break opportunities to a fresh assembled job, before compile."""
import argparse
import json
from pathlib import Path
import re

PREFIX = br'\noindent\textit{Source reference.}'
SOURCE = re.compile(br'(: )(.+?)(, source lines [0-9]+--[0-9]+\.)')
SLASH = re.compile(br'/(?!\\allowbreak\{\})')


def format_job(job):
    job = Path(job).resolve()
    state = json.loads((job / 'job-state.json').read_text())
    if (state.get('status') != 'assembled' or state.get('compile_run_id')
            or any((job / state[key]).exists()
                   for key in ('build_root', 'receipt_root') if key in state)):
        raise ValueError('Expected a fresh assembled job; compiled jobs cannot be edited')
    package = job / state['package']
    rows = json.loads((package / 'manifest.json').read_text())['items']
    if any((package / row['compile_receipt']).exists() for row in rows):
        raise ValueError('Compile receipt exists; compiled jobs cannot be edited')
    changed = 0
    for row in rows:
        path = package / row['item_path']
        original = path.read_bytes()
        lines = original.splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith(PREFIX):
                lines[index] = SOURCE.sub(
                    lambda match: match[1] + SLASH.sub(lambda _: br'/\allowbreak{}', match[2]) + match[3],
                    line, count=1)
        updated = b''.join(lines)
        if updated != original:
            path.write_bytes(updated)
            changed += 1
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', type=Path, required=True)
    args = parser.parse_args()
    try:
        changed = format_job(args.job)
    except ValueError as error:
        parser.error(str(error))
    print(f'Formatted source pointers in {changed} item(s)')


if __name__ == '__main__':
    main()
