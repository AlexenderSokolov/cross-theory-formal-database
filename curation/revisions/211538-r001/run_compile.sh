#!/usr/bin/env bash
set -euo pipefail
revision_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$revision_dir/../../.." && pwd)"
python_exe="${PYTHON_EXE:-python}"
work_dir="${REVISION_WORK:?Set REVISION_WORK outside the repository for build and receipts}"
export PYTHONUTF8=1
platform="$("$python_exe" -c 'import os; print(os.name)')"
if [[ "$platform" == "nt" ]]; then
  engine="$repo_dir/corpus-work/scripts/latexmk_xelatex.cmd"
else
  engine="$repo_dir/corpus-work/scripts/latexmk_xelatex.sh"
  chmod +x "$engine"
fi
package="$revision_dir/package-root"
"$python_exe" "$repo_dir/corpus-work/scripts/compile_editable_delivery.py" \
  --package "$package" --build-root "$work_dir/build" --receipt-root "$work_dir/receipts" \
  --item 211538 --engine "$engine"
"$python_exe" - "$package" "$work_dir" <<'PY'
from pathlib import Path
import hashlib,json,shutil,sys
package=Path(sys.argv[1]);work=Path(sys.argv[2])
r=json.loads((work/'receipts/211538.json').read_text(encoding='utf8'))
assert r['ok'] is True and r['passes']>=2
for key in ('pdf_path','compiler_log_path'):r[key]=r[key].replace(chr(92),'/')
(package/'receipts').mkdir(exist_ok=True)
(package/'receipts/211538.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
m=json.loads((package/'manifest.json').read_text(encoding='utf8'));row=m['items'][0]
assert row['tex_sha256']==r['input_sha256']
row['status']='verified_editable_tex';m['verified_count']=1
(package/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(package/'sources/211538/provenance.json').write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
e=json.loads((package/'delivery-evidence.json').read_text(encoding='utf8'))
e['package_manifest_sha256']=hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest()
(package/'delivery-evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
(package/'pdf').mkdir(exist_ok=True)
shutil.copyfile(work/'build'/r['pdf_path'],package/'pdf/211538.pdf')
PY
"$python_exe" "$package/rebuild_database.py"
"$python_exe" "$repo_dir/corpus-work/scripts/validate_corpus.py" \
  --mode editable-delivery --package "$package" --source-root "$package" \
  --build-root "$work_dir/build" --receipt-root "$work_dir/receipts" \
  --evidence "$package/delivery-evidence.json" --item 211538 --report "$revision_dir/gate-result.json"
