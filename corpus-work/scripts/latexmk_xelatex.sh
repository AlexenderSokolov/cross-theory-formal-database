#!/usr/bin/env bash
set -euo pipefail
# A real engine invocation is required even on the second stable pass.
exec latexmk -xelatex -g "$@"
