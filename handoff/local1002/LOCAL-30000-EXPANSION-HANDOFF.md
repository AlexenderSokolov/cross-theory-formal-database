# Continue the corpus locally toward 30,000

The current fixed release candidate contains **1,002 locally qualified primary problem/proof units**, with 27 additions to the root-qualified safe 975 base. 30,000 is a future target. The original 3,000+ candidate catalog is a separate inventory, not a qualified count; preserve it separately and reconcile its exact census using the controller's catalog handoff. No additional source intake is included here.

Remote publication is a separate fact. The safe 975 planned tree is `669d8b47233a11ae40e8a7f4508f5b67df5274fb`; its actual verified commit was not available when this handoff was prepared. The sole publisher must supply the actual commit/tree/ref readback. This package does not claim that 1,002 or 30,000 problems are on GitHub.

## Files and current evidence

The controller should place `assembled-package/` at `editable-corpus/` and `portable-runtime/corpus-work/` at `corpus-work/`. `assembled-build/` is an optional retained historical build sidecar, not source code to execute. All declared sources used by the retained proof are package-relative or inline; old absolute `/tmp` paths in provenance are historical witnesses, not extra inputs to download.

`PORTABLE-SAFE-HANDOFF-INVENTORY.json` records the publication-relative path, length, SHA256, Git blob SHA1 and mode of every current public package/runtime file. Retained build artifacts have a separate inventory. No tar/zip was created because assembly allocation was capped at 160 MiB; the files are materialized and inventoried, not merely proposed.

`manifest.json` has exactly 1,002 unique stable IDs; `delivery-evidence.json`, `INDEX.md`, complete TeX, source carriers, original licensed PDFs, assets, notices, receipts and constrained SQLite are aligned. The current origin classes are 972 human-authored native TeX units, 24 checked published transcriptions and 6 human-authored proof-assistant transcriptions. Tiers are H1=92, H2=634, H3=276. These are root-reviewed source/material classifications, not independent mathematical correctness certificates.

Actual new-item CLI executions and current whole-package aggregate results are separately recorded. Exact 975 row/evidence/material/build/runtime/INDEX/SQLite identities were reconciled against safe 975r004. Its five changed licensing witnesses use the latest successful safe-witness reports; they are not silently inherited from the older raw-HTML version. Historical retained checks are never described as fresh 975 calls.

## Dependencies

The recorded environment is Linux, Python 3.12.14, pypdf 6.10.0, SQLite through Python's sqlite3, XeTeX/TeX Live 2025/dev (Debian), xdvipdfmx, Poppler pdftotext/pdftoppm, Noto Serif CJK SC, Latin Modern, AMS/Xy and the genuine packages used by the articles. `corpus-work/ENVIRONMENT_SNAPSHOT.json` and runtime inventory provide the exact recorded pins. Install dependencies from official vendor/package sources locally; this handoff does not install or download anything automatically. Other platforms or TeX versions need fresh validation and layout comparison.

All current receipts name XeLaTeX. Genuine IEEEtrantools 1.5 for 1505 is supplied and declared at `editable-corpus/sources/1505/runtime/IEEEtrantools.sty`. Include that directory in TEXINPUTS when rebuilding. Do not replace missing genuine packages with invented macros, execute private publisher classes/archives, or enable shell escape to work around a failure.

## Restore or rebuild SQLite

The isolated local package contains an uncompressed full-text SQLite database (67,211,264 bytes before any final metadata-only source-locator update). Its exact current hash is in the inventory and database-delivery metadata. All 1,002 full TeX strings, source fields, locators, integrity and foreign keys were checked.

For this **local uncompressed** package, rebuild into a separate working directory; do not overwrite immutable/hardlinked release inputs:

```bash
mkdir -p local-state
python3 editable-corpus/rebuild_database.py --output "$PWD/local-state/corpus.sqlite"
```

The helper's VACUUM may need space for a second database and journal. The cloud preparation used a pinned local memory-temp/journal wrapper to stay within its allocation cap. A 30,000-item database will be substantially larger; plan local disk space rather than extrapolating this limit.

For a future **publisher-created chunked Git release**, use its actual final `database-delivery.json` and ordered parts, then:

```bash
python3 editable-corpus/restore_database.py --help
```

Use the release-specific supported arguments and verify its restored SHA256. The current local metadata does not describe a 1,002-item chunked release, and the five old 975 chunks were deliberately not copied into the current 1,002 namespace. The publisher still needs to create and independently restore the final 1,002 delivery before publishing it.

## Validate using retained builds or fresh local builds

From the checkout root, a complete retained build sidecar can be checked without recompilation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 corpus-work/scripts/validate_corpus.py \
  --mode editable-delivery --package editable-corpus \
  --evidence editable-corpus/delivery-evidence.json \
  --build-root retained-build --report local-state/aggregate.json
```

If retained builds are not delivered, compile into new external directories and use the newly generated receipts:

```bash
mkdir -p local-state/fresh-build local-state/fresh-receipts
TEXINPUTS="$PWD/editable-corpus/sources/1505/runtime//:" \
PYTHONDONTWRITEBYTECODE=1 python3 corpus-work/scripts/compile_editable_delivery.py \
  --package editable-corpus --build-root local-state/fresh-build \
  --receipt-root local-state/fresh-receipts --engine xelatex
PYTHONDONTWRITEBYTECODE=1 python3 corpus-work/scripts/validate_corpus.py \
  --mode editable-delivery --package editable-corpus \
  --evidence editable-corpus/delivery-evidence.json \
  --build-root local-state/fresh-build --receipt-root local-state/fresh-receipts \
  --report local-state/fresh-aggregate.json
```

For one item, pass `--item ID` to both commands. Preserve original receipts/builds and failures. A new environment's successful compilation is new evidence, not byte equality to an old compiler log or a replacement for source/layout QA. Review all selected pages against the licensed original and retain actual warnings and source quirks.

## Canonical batch format and expansion loop

A reviewed normalization batch has a sealed `ready-group-*.json`, exact approved/eligible original IDs, package/build roots, full item rows and per-item delivery evidence, positive `package_files_sha256`, actual build artifact pins, isolated aggregate QA and fixed validator/schema hashes. Handoffs are immutable: corrections receive new revisions and explicit overlays.

Each manifest row needs stable problem_id, title, human author/work, exact source/version, grant/notice paths, origin class, explicit H1/H2/H3 rationale, flattened complete editable TeX/hash, primary/context/source locators, declared licensed assets and real stable compile receipt. Delivery evidence binds the complete statement/proof/context to actual licensed carriers with source indices/line or byte spans, source hashes, fidelity receipts and a unique claim key. The constrained SQLite stores full TeX rather than links or truncated snippets. Manifest and per-ID provenance must agree exactly.

For every future batch:

1. Resolve an exact human-authored source version and component-specific reuse rights. Keep nonexclusive/unlicensed native aids, archives, publisher classes and private preambles private and unexecuted. Export minimal factual licensing evidence, never scraped HTML containing request/session fields.
2. Select a distinct complete authored primary outcome, its full proof and required context/new source-local core. Give a concrete difficulty rationale. Helpers, consequences, parameter variants and supporting statements count zero. Do not create mathematics, repair source formulas or weaken a target to force admission.
3. Perform source-interface and semantic dedup review. Same article can contain genuinely different selected outcomes, but file count or ID order does not prove distinctness. Unresolved interfaces stay held.
4. Normalize only the approved material, render and compare all relevant pages, record every actual pass/diagnostic and declared finite layout/reference adaptation. Preserve source quirks and failed attempts.
5. Seal a positive public allowlist and packet hashes; run explicit item checks, full merged aggregate, constrained full-text SQLite/INDEX/source projections and independent restore. A source-ready or collector-ready record alone is not qualification.
6. Lock the exact intake, integrate in an isolated staging directory, reconcile retained historical identities and run fresh checks for new/changed items plus a fresh full aggregate. No count padding or silent milestone bypass. The supplied policy adapter permits only the explicit real 975→1002 transition; do not reuse its hardcoded counts for future milestones.
7. Only the authorized publisher updates Git after all gates. Verify actual commit, tree and ref readback, then update the remotely published count separately.

## Mandatory current exceptions and pending release gates

Keep every source-scope override from the fixed intake and root decisions. Required examples include 2467's complete diagnostic addendum (including its disclosed Underfull10000), 1912's four locator repairs, 1903's actual two canonical passes, 1256's mixed checked-published body/editable diagram-label treatment, and exact-version evidence rather than generic contents-list URLs for 2497/2527. Strict checked-published origins must not be relabeled as licensed native sources.

Current attribution corrections 2589/2535r003 and 2569r002 remain mandatory. The 1536/1538 common source-level CC3 locator is unified while each item's current adaptation disclosure is preserved. Copied inapplicable 1543 conference-branch clauses were removed from current 1538/1545 notices; historical originals remain explicitly historical, and the true 1543 clause remains. Safe minimal notices replace all six known session-bearing licensing witnesses; raw originals are private and never public history.

1318's l=1 versus cited l>=2 and intermediate i=0 source interfaces remain held; no mathematics was repaired. Other noncounting holds and source-only later admissions stay outside this fixed release. Newer 1558/1559/1561 are not included here. The original candidate catalog may contain further eligible, held or unreviewed records; none receives automatic qualified credit.

Before claiming a GitHub 1,002 release, the publisher must bind the actual safe975 commit/tree, independently audit the final 1,002 file/object/tree plan, create and restore its final database delivery, repeat any checks whose actual inputs change, inspect export hygiene and verify the real Git ref/commit/tree. Local qualification and a source catalog are insufficient to claim 30,000 completed problems.
