# Project workflow: editable human-proof corpus

Run from the corpus project root. The dated local example below uses an immutable package and existing artifacts. Validation reports are written outside the package; validation does not admit candidates, change SQLite or publish remotely.

## Dated local frozen example (2026-10-02 UTC; historical uncompressed transport)

- Package: `publication/tex-remediation-20261002/frozen-377-v3`
- Existing derived evidence sidecar: `audit/root-derived377-v3-20261002-0528.json`
- Matching actual admission artifacts: `publication/tex-remediation-20261002/release-build-377-v3`
- Archived receipts: the package's per-item receipt paths; no external receipt override in this example

The sidecar is checked against the package manifest hash and carries retained excerpt/fidelity witnesses. It preserves bounded existing source checks; it is not a new mathematical review. This example uses the existing sidecar without regenerating or editing it.

## Current read-only application

```sh
PACKAGE=publication/tex-remediation-20261002/frozen-377-v3
EVIDENCE=audit/root-derived377-v3-20261002-0528.json
BUILD=publication/tex-remediation-20261002/release-build-377-v3
REPORTS=candidates/verified-corpus-skill/records

PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_corpus.py \
  --mode editable-delivery --package "$PACKAGE" --evidence "$EVIDENCE" \
  --build-root "$BUILD" --item 001 --report "$REPORTS/green-item-001-report.json"
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_corpus.py \
  --mode editable-delivery --package "$PACKAGE" --evidence "$EVIDENCE" \
  --build-root "$BUILD" --report "$REPORTS/green-package-report.json"
```

Reports must be outside the read-only package. Success requires exit 0, no global errors, no failed items, and the correct `editable_qualified_count`. The item route still checks the entire package's manifest, INDEX and SQLite consistency; it only applies the body/compile gate to the selected item. The aggregate is mandatory before claiming the package passes. Neither result changes a remote delivered count.

Inspect the actual final engine invocation in each bound aggregate `compiler.log`, not merely receipt warning arrays. Earlier-pass warnings can resolve; final label/reference/bookmark/outlines/PageLabels rerun requests or multiply-defined labels fail. The compiler makes at least two and at most four actual passes; never edit a receipt to imply extra passes happened.

## Checkout portability and authorized regeneration

Admission PDFs/logs are external to this frozen package. A remote checkout does not acquire them automatically. Publish the portable evidence sidecar with the package and regenerate compilation outside the package when that work is authorized:

Current compressed-database packages include `database-delivery.json` and either one `corpus.sqlite.gz` file (v1) or every ordered file in `database-parts` (v2). Download all declared parts before restoring; hashes and order are checked. Before validation, run the bundled no-download restore helper. It verifies both hashes, SQLite integrity, foreign keys, item count and exact TeX full text, and refuses to replace a differing existing file. The dated377 example above predates this transport and remains an uncompressed historical example.

```sh
if [ -f "$PACKAGE/database-delivery.json" ]; then
  python3 "$PACKAGE/restore_database.py"
fi
```

The v1 restore step is backed by the exact restored506 checkout gate and seven gzip-adapter tests; v2 is additionally backed by 27 adapter tests and an exact complete 756-row three-part roundtrip with full-text/integrity/FK checks and the literal offline command. It is a bounded documentation update, not a new independent behavioral skill evaluation. Set `PACKAGE` to the current checkout package before using it.

```sh
python3 scripts/compile_editable_delivery.py --package PACKAGE \
  --build-root EXTERNAL_BUILD --receipt-root EXTERNAL_RECEIPTS
python3 scripts/validate_corpus.py --mode editable-delivery --package PACKAGE \
  --evidence PACKAGE/delivery-evidence.json --build-root EXTERNAL_BUILD \
  --receipt-root EXTERNAL_RECEIPTS --report EXTERNAL_REPORT.json
```

Uppercase paths in this second example are placeholders, not the verified command. XeLaTeX, required fonts/packages and pypdf must already be installed. The helper installs/downloads nothing. Preserve archived package receipts; the override selects fresh external receipts. Missing artifacts, assets or prerequisites remain failures.

## Historical inspection boundary

`python3 scripts/validate_corpus.py --item 001` is the old active-skill command, observed to exit 1 with mode `unspecified` and editable count 0. Explicit `--mode historical-evidence` retains legacy inspection, whose `qualified_count` may include PDF-page wrappers and cannot establish editable delivery. It writes a report by default; use an explicit isolated report path if historical inspection is separately authorized. No historical admission or compilation was run in this repair.

## Suite and publication boundary

Run `python3 -m unittest discover -s tests -v` with an isolated `TMPDIR` and bytecode disabled for this bounded check. The test record names observed failures/skips, rather than assuming earlier test claims are current.

The authorized publisher must separately confirm the exact remote commit, manifest, INDEX and TeX hashes. Prefer a full remote SQLite readback and check its integrity, foreign keys, complete TeX content and count. If the connector cannot fetch the published binary (for example, an inline-content size limit), compare the exact remote Git blob identity with the locally integrity/foreign-key/full-text/count-checked SQLite bytes. Record the commit, blob identity and local checks; describe the result as hash-only remote database verification, not a remote SQL query or full binary readback. A pending upload remains pending regardless of local checks.
