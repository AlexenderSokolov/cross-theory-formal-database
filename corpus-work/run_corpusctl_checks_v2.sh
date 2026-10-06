#!/bin/sh
# Focused controller v2 fixtures. Does not run corpus gates or mathematical production.
set -eu
work=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH= cd -- "$work/../.." && pwd)
export PYTHONPATH="$work/scripts:$root/repo/editable-corpus${PYTHONPATH:+:$PYTHONPATH}"
for test in test_runtime_owner_recovery.py test_batch_v2.py test_release_step_resume.py test_publish_recovery.py test_transport_resume.py test_delta_staging.py test_stage_cli.py; do
 "$root/runtime/python/bin/python" -B "$work/scripts/tests/$test"
done
