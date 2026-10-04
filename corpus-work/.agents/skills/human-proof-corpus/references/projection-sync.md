# Reviewed editable-package projection synchronization

This candidate prepares mechanical projections for an externally reviewed manifest. It does not create source/body/comparison witnesses, proofs, H/rights/admission decisions, or remote delivery claims. The input package remains unchanged; outputs must be new directories and remain available after failure.

## Exact input contract

Supply the externally reviewed `manifest.json` SHA-256 and an independently pinned `HELPER_PINS.json`. The pin record fixes all five canonical package helpers and the three checking programs. The example manifest pin is `5d77a2bba2465082e282e3aa9e874ee51ffeaeaa238792cf2bcc47142b8ea1da`; the pin-record hash is `bb792456e25db16141b8f8369809940e0a6ade483bbd029f7a6497d884fa9252`. Computing a fresh digest is not evidence of review or permission.

The script requires existing complete item evidence, current TeX/assets hashes, valid source/body/comparison declarations, compatible schema, and successful existing compile receipts. Receipts check declared input/assets/PDF/log hashes and recorded warning fields; actual PDF/log bytes and the full delivery gate still require the explicit external build and receipt roots. The script performs no fresh compilation.

Only provenance JSON, the five-column INDEX, canonical fixed helpers, the existing evidence `package_manifest_sha256`, and SQLite are projected. The original manifest, full editable TeX, sources, licences, assets, compile receipts, and all item evidence declarations are preserved. The canonical API is `rebuild(root, output)` and populates complete source/problem rows including full `tex_content`; the canonical rebuild CLI accepts only `--output`, with its root resolved from its own script. There is no `--package` argument for that CLI.

## Prepare a fresh output

Run on Yupeng from `/disks/sata1/yupeng/human-proof-corpus`, passing a never-used output path:

```sh
bash candidates/reusable-projection-sync-r001/run_projection_sync.sh \
  --package snapshots/admitted1499-metadata-r001 \
  --manifest-sha256 5d77a2bba2465082e282e3aa9e874ee51ffeaeaa238792cf2bcc47142b8ea1da \
  --master-helpers repo/editable-corpus \
  --helper-pins candidates/reusable-projection-sync-r001/HELPER_PINS.json \
  --helper-pins-sha256 bb792456e25db16141b8f8369809940e0a6ade483bbd029f7a6497d884fa9252 \
  --output candidates/reusable-projection-sync-r001/YOUR_FRESH_OUTPUT
```

`PROJECTION_PREPARATION.json` means prepared projections only. Invoke `repo/corpus-work/scripts/validate_corpus.py --mode editable-delivery` separately with explicit `--package`, `--evidence`, actual `--build-root`, actual `--receipt-root`, and an independent `--report`; use `--item ID` for the item gate, then omit it for the aggregate. Root merge/public restoration belongs to the main owner.

## Targeted retained trial

```sh
bash candidates/reusable-projection-sync-r001/run_projection_checks.sh \
  --trial-dir candidates/reusable-projection-sync-r001/YOUR_FRESH_TRIAL
```

The test entrypoint rejects an existing directory before writing. Each run retains input negative fixtures, output package, stdout/stderr, exact command records, actual gate reports, and summary under its own trial directory. It uses the real 1499 metadata-only snapshot, changes no mathematical body, checks every source/problem SQL field and full text, checks provenance/INDEX and immutable byte inventories, and tests six failures: wrong manifest pin, duplicate ID, conflicting source metadata, failed compile receipt, wrong source-body hash, and preserved existing different output.

The existing `reports/ACTUAL_TRIAL_R001.json` and successful original run are preserved. `trial-r002/reports/ACTUAL_TRIAL_R001.json` records the repeatable-entrypoint verification: positive trial and both actual delivery gates passed, each gate qualified one item with zero errors, and all six negative cases were rejected as expected. The existing actual two-pass build/receipts from `candidates/server-workers/parallel12-r001/worker-07-1499/{build-r004,receipts-r004}` were reused. No fresh compilation, main/Git modification, mathematical certification, rights review, root admission, publication, or delivered-count increment occurred.

`reports/TECHNICAL_READINESS_R002.json` binds the independently checked current candidate, real input/output package, complete SQLite projection and actual trial evidence to their hashes. Readiness applies to this retained one-item trial and mechanical preparation, not unseen packages.

生产通用入口是 `corpus-work/scripts/sync_editable_projections.py` 或 `corpus-work/run_projection_sync.sh`，上述candidate路径仅真实保留样本，不是任何包的默认批准。母本测试入口仅适用于该已保留1499夹具；通用使用都须显式实际审定pins/新输出和后续逐题门禁。
