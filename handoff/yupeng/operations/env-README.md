# Project runtime and isolated engineering gates

The runtime is confined to `/disks/sata1/yupeng/human-proof-corpus/runtime`. No shell startup files, global proxy configuration, user credentials or host fonts are changed.

## Reproduce the runtime

`bash /disks/sata1/yupeng/human-proof-corpus/operations/env-install.sh > /disks/sata1/yupeng/human-proof-corpus/reports/env-texlive-install.log 2>&1`

The installer uses the frozen official TeX Live 2025 final repository at `https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2025/tlnet-final`. Python is a venv from the existing Anaconda Python 3.13.9; `reports/env-python-freeze.txt` pins installed packages and `runtime/downloads/python-wheels` retains their distribution archives. The installer archive, fonts, downloaded wheel hashes, TeX package revisions and actual logs are retained in the runtime/reports directories. TeX install documentation/source package files are omitted; editable corpus source files are unaffected.

## Compile a single item

```bash
project=/disks/sata1/yupeng/human-proof-corpus
"$project/runtime/bin/compile-isolated" \
  --package "$project/repo/editable-corpus" \
  --build-root "$project/builds/worker-baseline" \
  --receipt-root "$project/receipts/worker-baseline" \
  --item 001 --engine xelatex --timeout 180
```

This wrapper executes the complete trusted `compile_editable_delivery.py` Python process inside bubblewrap, with network/PID/mount/IPC isolation, a cleared environment, a read-only project/runtime and only the declared output directories writable. It retains all absolute package/build/receipt paths. Each build root has separate HOME/cache/TEXMFVAR/TEXMFCONFIG/tmp directories. Use a different build and receipt root for every concurrent worker.

The wrapper constructs TEXINPUTS from the selected item's declared `.sty`/`.cls`/`.def`/`.fd` manifest assets, preserving exact required author macro versions. Official Noto Serif and Noto Sans Math binaries are mapped inside the sandbox to the historical `/usr/share/fonts/truetype/noto/` lookup path. This does not rename fonts, substitute another family or write to the host font directory.

Other trusted corpus engineering scripts may use `operations/env-isolated.sh SCRIPT [ARGS]` with explicit `--package`, `--build-root`, `--receipt-root`. Optional `--report`/`--json-report`/`--report-file` output parents must stay in project `reports`. In all cases files may only resolve inside this project. The user's existing Anaconda standard library and its required shared libraries are read-only; global Anaconda site-packages are hidden, and personal home/credential directories are never mounted.

## Evidence and limitations

`reports/env-isolation-probe.json` is an actual offline/read-only/credential-visibility import probe, not a TeX compilation result. Only receipt JSON with `ok=true`, a fresh PDF and retained compiler logs establish an item's compile result. The runtime depends on this server's existing glibc, Poppler, system fonts and Anaconda stdlib/shared libraries; record their actual versions before accepting fresh results. Moving to a different machine or changing a runtime/font/macro requires the affected gates again.

## Single-item input view (r003)

Compilation requires explicit `--item`. The entry directory is presented at the same absolute package path as a read-only view containing hard links to the original entry and its declared neighboring assets. Unrelated items and their local runtime files cannot shadow the selected item's standard TeX packages. Full validators continue to read the complete package. No core compile/validation gate or author input bytes are changed. The official DejaVu 2.37 math font is supplied under its real DejaVu Math TeX Gyre name. `reports/env-launcher-r003.json` links successful 293/551/1505/561 compiles and a deliberately undeclared authentic figure negative fixture; the fixture is an engineering test and is never counted as a corpus item.

`env-check-tex.py --package PACKAGE [--package PACKAGE] --report REPORT` checks explicit style/class and TikZ/PGF/PGFPlots/TCB libraries through actual kpse lookup. TikZ's documented PGF-file fallback is respected. It records unexpanded dynamic expressions and does not replace fresh per-item compilation.

The frozen TeX repository currently reports a valid signature with an expired signing key, so tlmgr prints `not verified`. No signature check option is disabled. Keep this actual limitation with the installer logs and hashes; do not claim current GPG validation.
