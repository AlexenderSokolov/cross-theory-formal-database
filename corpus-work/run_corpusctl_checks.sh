#!/bin/sh
# Run after a related implementation change; never a per-problem production step.
set -eu
work=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$work/../.." && pwd)
for test in test_corpus_runtime.py test_corpus_batch.py test_controller_publish.py; do
 "$root/runtime/python/bin/python" -B "$work/tests/$test"
done
