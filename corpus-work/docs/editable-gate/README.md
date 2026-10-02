# Editable delivery gate

This is a read-only, opt-in extension of the existing corpus validator. It checks actual standalone editable TeX bodies, retained source/fidelity witnesses, declared independent problem units, reason-bearing admission holds, INDEX/manifest/provenance agreement, full-text SQLite, and current compilation evidence. It does not independently certify mathematical correctness, authorship, semantic uniqueness, or difficulty.

## Count distinction

- `--mode editable-delivery --package PACKAGE` is the current delivery route
- `--package PACKAGE` without a mode also selects editable delivery
- Legacy CLI inspection requires explicit `--mode historical-evidence`; its count is historical evidence only and can include PDF-page wrappers
- Bare legacy-style `--item ID` fails closed without publishing a historical report
- The imported legacy validation API is retained for internal recovery callers
- A local evidence-contract pass does not establish a GitHub commit or remote delivered count

## Portable package and compilation

Publish `delivery-evidence.json` alongside the package. It contains exact body hashes/ranges, source-version/locator witnesses, existing bounded comparison declarations, and preserved inline original native or previously checked transcription excerpts where a separate excerpt file is absent. File-backed witnesses point only to retained package files. Unsupported or missing source-map schemas remain explicit derivation holds.

Packaged receipts archive the admission run. Its matching PDFs/logs may live in a separate admission build directory; they are not automatically available in a GitHub checkout. Validation must either find those exact matching artifacts or use freshly regenerated receipts and artifacts. Do not report checkout-portable success from workspace-only builds.

With XeLaTeX, required TeX packages/fonts, and pypdf already installed, regenerate outside the read-only package:

```sh
python3 corpus-work/scripts/compile_editable_delivery.py --package editable-corpus --build-root .editable-build --receipt-root .editable-receipts
python3 corpus-work/scripts/validate_corpus.py --mode editable-delivery --package editable-corpus --evidence editable-corpus/delivery-evidence.json --build-root .editable-build --receipt-root .editable-receipts --report editable-delivery-report.json
```

The helper performs at least two and at most four successful `-no-shell-escape` passes, continuing while the final log requests label/reference/bookmark stabilization. It records the actual pass count and fails if stabilization is still requested at the bound. It installs/downloads nothing, rejects missing/changed assets and escaping paths, and preserves packaged receipts. The report explicitly names the receipt set. The package uses source-specific fonts, including Latin Modern and Noto Serif CJK SC, and source-specific TeX packages. Missing prerequisites remain compile failures.

For original admission receipts, omit `--receipt-root` and supply their matching `--build-root`. An explicit `--report` must be outside the package. Add `--item ID` for an individual gate; whole INDEX/SQLite consistency is still mandatory.

## Deriving evidence from existing records

Run from the corpus project root:

```sh
python3 scripts/derive_stacks_evidence.py --package PACKAGE --project-root . --bindings EXISTING_AHL_ALJABR_BINDINGS.json --bindings EXISTING_JEP_BINDINGS.json --output DELIVERY_EVIDENCE.json
```

The helper supports the observed exact Stacks reference adaptations, native excerpt line maps, original-asset-path changes, existing source-worker bindings, retained source-page hashes, and already reviewed transcription units. It records current mechanical byte bindings and preserves the original bounded-check declarations; it does not invent or backdate review. Initial derivation may use the existing source cache and source-worker artifacts. The published sidecar then carries the minimal portable witnesses needed for checkout validation.

Reason-bearing exclusions are pinned by `scripts/editable_exclusions.json` and `scripts/editable_gate_evidence/`. Optional additional exclusions cannot remove or override known holds. A cleared hold requires an explicit updated admission decision; short proof or corollary syntax alone is not a rejection rule.

## Verification scope

The isolated frozen251-v2 package passed the whole gate and all251 individual CLI invocations using its exact archived build artifacts. The169-test suite passed with no skips, including stabilization at three passes and failure at four still-unstable passes. A fresh checkout-style compile and override-receipt gate also passed for item001. This does not claim fresh recompilation of all251 or a new remote publication count.

The skill correction is a review-only proposal. Static regression checks and the observed PDF-wrapper acceptance regression support it; new agent pressure/scenario tests have not been run, and it is not deployed automatically.

## Final-pass stability check (2026-10-02 correction)

Two successful engine exits are a minimum, not evidence that labels or bookmarks have stabilized. The current validator checks the final engine invocation in the SHA256-bound aggregate compiler log, independently of missing or empty receipt warning fields. A final rerun request or multiply-defined label fails admission. Warnings from earlier passes that are resolved in the final pass do not fail it. The checkout compiler makes at least two and at most four passes and rejects remaining rerun requests or duplicate labels. Keep superseded receipts and frozen snapshots as historical records; do not rewrite them to imply extra passes happened.

Repeated overlapping source-context ranges can create duplicate TeX labels even when all original proof text is present. Correct this by retaining each complete original passage once with precise source mapping, then rebuilding and repinning a new immutable revision. Do not weaken evidence uniqueness checks to admit ambiguous body mappings.
