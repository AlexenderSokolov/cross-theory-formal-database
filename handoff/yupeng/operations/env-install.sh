#!/usr/bin/env bash
set -euo pipefail
root=${CORPUS_PROJECT_ROOT:-/disks/sata1/yupeng/human-proof-corpus}
runtime="$root/runtime"
reports="$root/reports"
repository=https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2025/tlnet-final
mkdir -p "$runtime/downloads" "$runtime/setup-home" "$runtime/fonts" "$reports"
# This script installs only into the project prefix; it does not modify shell startup files.
export HOME="$runtime/setup-home"
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
if [ ! -x "$runtime/python/bin/python" ]; then
 /disks/sata1/yupeng/anaconda3/bin/python3 -m venv --copies "$runtime/python"
fi
if [ -f "$reports/env-python-freeze.txt" ]; then
 "$runtime/python/bin/python" -m pip --isolated download --index-url https://pypi.org/simple --dest "$runtime/downloads/python-wheels" -r "$reports/env-python-freeze.txt"
 "$runtime/python/bin/python" -m pip --isolated install --no-index --find-links "$runtime/downloads/python-wheels" -r "$reports/env-python-freeze.txt"
fi
if [ ! -f "$runtime/downloads/install-tl-2025-final.tar.gz" ]; then
 curl --noproxy '*' --fail --location --retry 3 "$repository/install-tl-unx.tar.gz" -o "$runtime/downloads/install-tl-2025-final.tar.gz"
fi
sha256sum "$runtime/downloads/install-tl-2025-final.tar.gz" > "$reports/env-installer.sha256"
mkdir -p "$runtime/texlive-installer"
tar -xzf "$runtime/downloads/install-tl-2025-final.tar.gz" --strip-components=1 -C "$runtime/texlive-installer"
cat > "$runtime/texlive.profile" <<PROFILE
selected_scheme scheme-small
TEXDIR $runtime/texlive/2025
TEXMFCONFIG $runtime/setup-home/texmf-config
TEXMFHOME $runtime/setup-home/texmf
TEXMFLOCAL $runtime/texlive/texmf-local
TEXMFSYSCONFIG $runtime/texlive/2025/texmf-config
TEXMFSYSVAR $runtime/texlive/2025/texmf-var
TEXMFVAR $runtime/setup-home/texmf-var
binary_x86_64-linux 1
instopt_adjustpath 0
instopt_portable 1
instopt_write18_restricted 0
tlpdbopt_install_docfiles 0
tlpdbopt_install_srcfiles 0
PROFILE
if [ ! -x "$runtime/texlive/2025/bin/x86_64-linux/xelatex" ]; then
 perl "$runtime/texlive-installer/install-tl" -no-gui -profile "$runtime/texlive.profile" -repository "$repository"
fi
texbin="$runtime/texlive/2025/bin/x86_64-linux"
"$texbin/tlmgr" option repository "$repository"
mapfile -t packages < "$runtime/texlive-packages.txt"
"$texbin/tlmgr" install "${packages[@]}"
for family in Regular Italic Bold BoldItalic; do
 curl --noproxy '*' --fail --location --retry 3 "https://raw.githubusercontent.com/notofonts/noto-fonts/ffebf8c1ee449e544955a7e813c54f9b73848eac/hinted/ttf/NotoSerif/NotoSerif-$family.ttf" -o "$runtime/fonts/NotoSerif-$family.ttf"
done
curl --noproxy '*' --fail --location --retry 3 https://raw.githubusercontent.com/notofonts/noto-fonts/ffebf8c1ee449e544955a7e813c54f9b73848eac/LICENSE -o "$runtime/fonts/NotoSerif-LICENSE.txt"
curl --noproxy '*' --fail --location --retry 3 https://raw.githubusercontent.com/notofonts/noto-fonts/ffebf8c1ee449e544955a7e813c54f9b73848eac/hinted/ttf/NotoSansMath/NotoSansMath-Regular.ttf -o "$runtime/fonts/NotoSansMath-Regular.ttf"
curl --noproxy '*' --fail --location --retry 3 https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.tar.bz2 -o "$runtime/downloads/dejavu-fonts-ttf-2.37.tar.bz2"
"$runtime/python/bin/python" - "$runtime" <<'FONT_PY'
from pathlib import Path
import tarfile,sys
runtime=Path(sys.argv[1])
with tarfile.open(runtime/'downloads/dejavu-fonts-ttf-2.37.tar.bz2','r:bz2') as tar:
 members={Path(m.name).name:m for m in tar.getmembers() if m.isfile()}
 for source,target in [('DejaVuMathTeXGyre.ttf','DejaVuMathTeXGyre.ttf'),('LICENSE','DejaVu-LICENSE.txt')]:
  (runtime/'fonts'/target).write_bytes(tar.extractfile(members[source]).read())
FONT_PY
"$texbin/tlmgr" --version > "$reports/env-texlive-version.txt"
"$runtime/python/bin/python" "$root/operations/env-capture.py"
"$texbin/xelatex" --version > "$reports/env-xelatex-version.txt"
"$texbin/latexmk" --version > "$reports/env-latexmk-version.txt"
find "$runtime/downloads" "$runtime/fonts" -type f -print0 | sort -z | xargs -0 sha256sum > "$reports/env-downloads.sha256"
sha256sum "$runtime/texlive/2025/tlpkg/texlive.tlpdb" > "$reports/env-texlive-tlpdb.sha256"
du -sh "$runtime" > "$reports/env-runtime-size.txt"
printf 'RUNTIME_INSTALL_DONE\n'
