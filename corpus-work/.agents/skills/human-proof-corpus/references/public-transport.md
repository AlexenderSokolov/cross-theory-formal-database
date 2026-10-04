# Thin exact-public transport reuse

`prepare_public_transport.py` prepares a new package from an externally reviewed explicit filelist. Identical paths/size/SHA may be copied with `copy2` from the cache of an earlier **actual public full restoration**; new or changed paths are downloaded without credentials from the fixed repository at the exact 40-character commit. It does not execute SQL/artifact recovery, gates, TeX, Git, Release APIs, admission or count changes.

## Inputs and evidence boundary

The owner supplies current commit and filelist SHA, old commit/filelist SHA, old actual public-proof SHA, the original actual cache root, and a never-used output directory. There is no inferred approval from a locally computed current manifest/filelist digest. Current file bytes are bound by the externally fixed filelist; its global status text is not used as a substitute for review.

The old proof must bind that old commit and filelist, actual full SQL integrity/projection, five successful restore/test/artifact/full-gate commands with hash-bound logs, and the hash-bound complete gate. The old cache path must match the actual command scope. Existing 1035 schema1 and 1040 artifact-chain proof formats are supported. Renamed cache roots require separately reviewed evidence; arbitrary prepared/local/test receipts cannot authorize production reuse. Only reusable listed paths are read; undeclared cache files, restored raw SQLite and cache-only diagnostics are not copied.

Every reused source must be a regular file without symlink ancestors and match its old/current approved size/SHA before output creation. `copy2` and destination verification preserve the input cache and prevent hardlink mutations. Noncanonical paths, file/directory collisions, duplicate JSON/path keys, directories and symlinks are rejected. Production URLs are constructed under `https://raw.githubusercontent.com/AlexenderSokolov/cross-theory-formal-database/COMMIT/editable-corpus/PATH`; redirects and size/SHA mismatches fail. No proxy credentials are used.

The new outer output contains `package/`, an exact `PUBLIC_FILELIST.json`, `TRANSFER_LEDGER.jsonl`, and `TRANSPORT_RECEIPT.json`. The ledger records each actually completed path, copy/download method, bytes/SHA, and exact download URL. Failure after output creation retains partial files and a failed receipt; preflight failures preserve existing paths. Reusing that output is rejected. Output itself is only prepared transport, never public restoration or qualification.

## Production invocation

Run from `/disks/sata1/yupeng/human-proof-corpus`. This example uses the reviewed 1040 filelist at checkpoint `4e3eff84cf43df6593bac0e07d86a3c068fcae30` and the earlier verified public1035 cache; substitute future identities only after external review:

```sh
bash repo/corpus-work/run_public_transport.sh \
  --commit 4e3eff84cf43df6593bac0e07d86a3c068fcae30 \
  --filelist repo/handoff/yupeng/release1040/PUBLIC_FILELIST.json \
  --filelist-sha256 8e4cea878ec404848848dd7ff33dcea06426a7a0cb9004cd771f478d455957f8 \
  --cache /disks/sata1/yupeng/human-proof-corpus/snapshots/release1035-public-restore-r001/package \
  --old-filelist repo/handoff/yupeng/release1035/PUBLIC_FILELIST.json \
  --old-filelist-sha256 48f0eea6e6829b645175c3bad09b233bf50ab2a3a5f32409826fb321a6991100 \
  --old-public-proof repo/handoff/yupeng/release1035/PUBLIC_RESTORATION.json \
  --old-public-proof-sha256 2d51d82399bbe508836851f15bc45fff4f87234f4aaa657081805193fe2f4e28 \
  --old-commit 61283eac8ee1341ae8afd354c4a40c2a0835ead4 \
  --output candidates/reusable-public-recovery-r001/YOUR_FRESH_OUTPUT
```

Then the root owner checks current source/program/helper identities, executes pinned standard database/artifact-chain recovery and the complete actual `editable-delivery` gate in the appropriate new directories. A prepared transport receipt never supplies that result. Canonical helpers and gates are unchanged by this candidate.

## Bounded verification already performed

```sh
bash repo/corpus-work/run_public_transport_checks.sh \
  --trial-dir candidates/reusable-public-recovery-r001/YOUR_FRESH_TRIAL
```

`trial-r001` uses a clearly identified ephemeral loopback HTTP fixture. Its positive case actually copied one unchanged old-cache file and downloaded one new file; the copy has a different inode. Thirteen negatives exercised tampered cache, wrong current/proof pins, old commit mismatch, preserved existing output, missing remote file with retained partial output, cached directory/symlink, duplicate/noncanonical paths, noncanonical test HTTP URL, redirect, and rejection of fixture proof in production. Synthetic proof and synthetic HTTP bytes are not public evidence. The fixture server stops at test completion and every trial directory is retained.

`reports/REAL_PUBLIC_SMALL_READBACK_R001.json` separately records actual unauthenticated reads of three exact current4e3 public files (`schema.sql`, `items/1499_alco_105.tex`, `database-delivery.json`): 43,034 bytes matching the fixed1040 filelist, plus one real old-public-cache `copy2`. Both real1035/1040 proof formats, command-log pins and complete gate reports were validated. This is small-scope transport evidence, not whole public fresh recovery.

Filelist-only planning predicts 1035→current1040 reuses 19,557 paths / 979,887,124 bytes and downloads 96 paths / 53,777,087 raw bytes. These are measured explicit-filelist sums, not an executed full transfer or elapsed-time claim. Current1040 files at the 3544051 public restoration and 4e3 checkpoint have the same approved filelist, so that existing actual cache would reuse all 19,653 paths; current full restore/gate responsibilities remain with root.

## Complete current1040 transport now executed

`full-current1040-transport-r001/package` contains all 19,653 declared files. The generic production entrypoint actually validated the old1040 proof, its five command-log pins and complete gate; checked every reusable cache path and every copied output size/SHA; copied all 1,033,664,211 bytes with `copy2`; and downloaded zero files because the previously restored3544051 public cache and reviewed current4e3 checkpoint share the exact approved filelist. Every copy has a distinct inode. The full ledger is `full-current1040-transport-r001/TRANSFER_LEDGER.jsonl`; its receipt is `TRANSPORT_RECEIPT.json`. The retained actual command and log identities are in `reports/FULL_CURRENT1040_TRANSPORT.json`; `run_full_current1040_transport_r001.py` records that one invocation.

This demonstrates the entire transport scope, including every path, rather than the earlier three-file readback. It does not execute a new SQL/artifact restore or full delivery gate. Root can now use this precise prepared package for the separately authorized standard recovery and gate; no TeX rebuild is required merely because unchanged verified transport bytes were copied.

## Reuse for the next25–100 checkpoint

Use the generic `run_public_transport.sh` with the next externally reviewed commit/filelist pin and the immediately preceding actual public-restoration cache/proof identities. The generic program contains no1035/1040 file-count assumptions; it supports the current count-bearing public-proof status families and schema1 or chained artifact-restoration evidence. Paths whose old and current declared size/SHA agree reuse that proven cache after actual byte validation; every new/changed path downloads from the next exact public commit. Supply a new output each time and retain its ledger. Never turn the last prepared transport receipt into an old public-restoration proof: only root's successful complete public SQL/artifact/gate result can authorize that future cache basis.

The current full-run evidence supersedes the earlier whole-transport gap while preserving the separate recovery/gate boundary. Independent code review passed in `reports/source-pool-resume-r002/TRANSPORT_READONLY_REVIEW.json` without rerunning green tests or changing the frozen generic code.
