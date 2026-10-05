#!/bin/sh
set -eu
B=/disks/sata1/yupeng/human-proof-corpus
OWNER=local-controller-01a10a85
GENERATION=1
if [ ! -f "$B/operations/corpusctl/FLOW.json" ]; then
 "$B/runtime/python/bin/python" -B "$B/repo/corpus-work/scripts/prepare_production_flow.py" --apply --owner "$OWNER" --generation "$GENERATION"
fi
for suffix in r003 r004 r005; do
 "$B/repo/corpus-work/corpusctl" --controller-id "$OWNER" --generation "$GENERATION" import-handoff --handoff "$B/candidates/native-source-continuous-$suffix/HANDOFF_STOPPED.json"
done
CORPUS_CONTROLLER_ID="$OWNER" CORPUS_CONTROLLER_GENERATION="$GENERATION" sh "$B/repo/corpus-work/run_corpusctl_service.sh" install
