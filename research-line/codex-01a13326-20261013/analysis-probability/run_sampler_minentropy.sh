#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
PY=/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python
"$PY" prepare_sampler_multicalibration.py
"$PY" prepare_minentropy_communication.py
"$PY" prepare_biased_linearity.py
"$PY" prepare_drops_assets.py ccc2025-11
"$PY" prepare_graph_matrix.py
"$PY" prepare_drops_assets.py ccc2025-35
"$PY" prepare_prg_avoidance.py
"$PY" prepare_drops_assets.py ccc2025-20
"$PY" prepare_counting_martingales.py
"$PY" prepare_drops_assets.py ccc2025-13 ccc2025-18
"$PY" prepare_stream_quantum.py
"$PY" prepare_drops_assets.py ccc2025-12
"$PY" prepare_noncollapsing_adversary.py
"$PY" prepare_drops_assets.py ccc2025-3
"$PY" prepare_quantum_threshold.py
"$PY" prepare_drops_assets.py ccc2025-23
"$PY" prepare_holant_hdx_codes.py odd-arity-holant-dichotomy
"$PY" prepare_drops_assets.py ccc2025-27
"$PY" prepare_holant_hdx_codes.py hdx-code-family-parameters
