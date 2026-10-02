---
name: human-proof-corpus
description: Use when collecting, admitting, validating, or recovering source-grounded mathematical problems with human-authored proofs in this corpus project.
---

# Human-proof corpus

Current completion means a unique independent problem with its actual full original human statement and proof in a standalone editable TeX file, traceable source evidence, H1/H2/H3 above ordinary PhD quals, fresh compilation, matching INDEX and full-text SQLite, and verified authorized GitHub delivery. File counts, source tags, difficulty labels, and historical success notes are not completion. Mechanical tools check evidence and compilation; they do not independently certify mathematics, authorship, difficulty or semantic uniqueness.

## Source screening

- Read the exact statement and every consecutive author proof in a pinned source revision. Match title, hypotheses, conclusion and claimed difficulty to that statement. A research chapter can contain elementary exercises; write a concrete above-ordinary-PhD-qual difficulty reason rather than labeling every extracted theorem advanced.
- Preserve author mathematics. Keep exact source excerpts, hashes, line ranges, author, version, retrieval date and license. Never invent source title, tag, locator or theorem attribution.
- Investigate “Omitted,” “left to the reader,” and missing author proof bodies. Reject omitted core reasoning. Original authors may present complete constructions before a theorem without a proof environment; use exact selected statement/proof/core ranges and source-bound fidelity evidence. Only use an explicitly authorized bounded omitted-detail exception after recording why the omitted detail is ancillary and the substantive author proof remains complete. Preserve the author's omission wording.
- Close local context: include referenced assumptions, equations, situation introductions and required adjacent statements; preserve ordinary external prerequisites as references. Keep each context's raw-file hash, exact line interval and excerpt hash. Check semantic uniqueness against existing claims, including different tags for equivalent results.

## Current editable-delivery workflow

1. Keep candidate work isolated from the active package. Read the actual source boundaries, original author text, necessary core support and current held/supporting-only decisions. Preserve stable IDs. A supporting result remains uncounted context; multiple formats or solutions of one claim still count once.
2. Embed the complete original statement, proof and necessary local support in each standalone TeX. Source PDFs and original figures may support provenance, but PDF-page wrappers, proof-page images, links, summaries and literal external proof inputs do not replace editable bodies. Retain original author organization, language, hypotheses and mathematical symbols; hold unresolved source ambiguities rather than repair them.
3. Record provenance and bounded source/fidelity checks tied to the exact delivered and source bytes. Portable pinned excerpts with original version/hash/locator evidence are valid; a full external original is not required when retained excerpts carry the necessary core. Use deterministic evidence derivation only for supported source-map schemas and existing source-check declarations. Unsupported or missing evidence stays held; derivation is not a new review.
4. Compile the final layout at least twice with no shell escape, and continue up to the four-pass stabilization bound if the final log requests reference/label/bookmark reruns. Record the actual successful pass count; fail at the bound if requests remain. Bind the actual input, required local assets, PDF and compiler-log hashes; retain old receipts when regenerating. Consult the recorder file to distinguish genuinely read assets from stale dependency residue. Require no unresolved references/citations or missing glyphs.
5. On an immutable package snapshot, require manifest and provenance agreement, unique IDs/claims, exact INDEX paths, SQLite integrity and source foreign keys, and exact full TeX in `problems.tex_content`. Run the opt-in route for each item and the whole package:

```sh
python3 scripts/derive_stacks_evidence.py --package PACKAGE --project-root . --output DELIVERY_EVIDENCE.json
python3 scripts/validate_corpus.py --mode editable-delivery --package PACKAGE --evidence DELIVERY_EVIDENCE.json --build-root BUILD --item ID --report ITEM_REPORT.json
python3 scripts/validate_corpus.py --mode editable-delivery --package PACKAGE --evidence DELIVERY_EVIDENCE.json --build-root BUILD --report DELIVERY_REPORT.json
python3 -m unittest discover -s tests -v
```

The derivation helper supports exact Stacks reference-only adaptation, explicit native excerpt line maps, existing source-worker bindings and retained source-page/transcription fidelity records. Read its derivation holds; use `--bindings` for the existing family-specific binding files. The published `delivery-evidence.json` must travel with the packet, including portable original excerpt witnesses and bounded existing checks. A checkout can validate that sidecar without the unpublished full source cache. Report paths must be outside the read-only package. Per-item validation still checks all package INDEX/SQLite consistency. Use `editable_qualified_count` with item failures and global errors; a report with failures is not a complete passing delivery.

Admission checks actual matching PDFs/logs in the explicitly selected build root. These workspace artifacts are not automatically present in a GitHub checkout. With installed XeLaTeX, required packages/fonts and pypdf, regenerate outside the package without changing its archived receipts:

```sh
python3 scripts/compile_editable_delivery.py --package PACKAGE --build-root .editable-build --receipt-root .editable-receipts
python3 scripts/validate_corpus.py --mode editable-delivery --package PACKAGE --evidence PACKAGE/delivery-evidence.json --build-root .editable-build --receipt-root .editable-receipts --report DELIVERY_REPORT.json
```

The report names the validated receipt set. Missing engine/packages/fonts/assets or failed passes stay failures; the helper installs or downloads nothing. Packaged-original receipt checks require their exact matching build artifacts; freshly regenerated receipt checks use the explicit external override. Do not claim portable gate success from workspace-only build evidence.

6. Serialize authorized publication through the exclusive publisher. After push, verify the exact remote commit and read back the published manifest, INDEX, TeX hashes and SQLite full-text count before reporting the delivered total. A local evidence-contract pass is not a remote count increase. Never let a collector or validator silently write active master state or publish to GitHub.

## Historical evidence-only workflow

The commands below retain the old `corpus/` manifest/admission API for recovery and historical evidence checks. Historical CLI inspection requires explicit `--mode historical-evidence`; its `qualified_count` is historical only and may include PDF-page wrappers. A bare legacy-style `--item` command fails closed. Supplying `--package` without a mode selects editable delivery. The imported legacy API remains available for internal recovery callers, and cannot establish current editable delivery or a completed GitHub publication.

Run from the project root. Stage extraction before assigning/admitting an ID:

```sh
python3 scripts/stacks_extract.py discover --out audit/candidates.jsonl
python3 scripts/stacks_extract.py extract TAG --spec SPEC.json --out-dir STAGING
python3 -m unittest discover -s tests -v
```

Read the staged item. Supply honest reviewed completeness/context fields, difficulty rationale and unique claim key. Convert paths to corpus-relative paths when promoting TeX, excerpts and metadata. Preserve original IDs; use new IDs of at least three digits without truncating 1000+.

Add candidate metadata to corpus/item_status.json under quarantined status. Compile before serial admission:

```sh
python3 scripts/compile_all.py --item ID
```

Require a fresh two-pass receipt with matching TeX, provenance/runtime-dependency and PDF hashes. Set active status and add the matching five-column INDEX row only after substantive review and compilation succeed. Then run:

```sh
python3 scripts/validate_corpus.py --mode historical-evidence --item ID
python3 scripts/validate_corpus.py --mode historical-evidence
```

On historical-gate failure, keep the item quarantined and remove its historical active INDEX row; preserve artifacts and explain the reason. Do not use old build PDFs or merely mark review booleans true to meet a target. Historical validation_report.json counts, INDEX labels and highest ID do not establish editable completion.

## Compilation and recovery

Compiler resource setup is workspace-local under .tex-cache: generated XeLaTeX format, official CTAN Latin Modern fonts, and AMS/LM/Xy font maps. The CLI configures these automatically. Missing ctex affects old Chinese wrappers, not newly reviewed English ones.

Inspect the fresh receipt's log. Check final-pass references; first-pass warnings may resolve on pass two. A TeX page count can precede an xdvipdfmx physical-font failure. Missing valid PDF remains failure.

Serialize global receipt, manifest and INDEX writes. Parallel workers may stage items but must not overwrite shared reports. Preserve legacy evidence in quarantine and rebuild active INDEX; never renumber away gaps or treat historical compile claims as current receipts. Use the validator/compiler schema and existing tests rather than adding model-judge or evaluator platforms.

## Ready queues and shared-state discipline

Collector drafts are not admission authorization. Publish an explicit final-only `ready-specs.json`, `ready-entries.json`, or `ready_metadata_paths.json` after source, core dependency, scope, and obvious semantic-duplicate checks. Keep unresolved candidates in a separate hold/draft file, with an `admission_hold` whenever they may otherwise reach staging. Do not rerun historical collector build scripts over a corrected ready list. Copy a reviewed snapshot for admission; source files already bound to an active receipt must remain byte-stable.

Use essential hypotheses in editorial titles: restricted quiver/graph classes, equal dimensions, characteristic, or the selected part of a theorem cannot silently disappear. A broad title can imply a theorem the included author never proved. Correct the title in metadata, TeX and INDEX, then obtain a fresh receipt and gate result.

Check known theorem identities across sources, not just tags or DOI strings. For example, the full Serre quotient construction from Stacks duplicated an already active AlJabr claim and was excluded; its proof could remain context for a genuinely different K-zero statement. Supporting claims on reproduced pages are not separately counted.

If a process session disappears, read the manifest and current hashes before retrying. The bounded admission queue skips qualified stable identities and reuses only current compile receipts. An empty result file is not evidence of success. Final qualification must still come from the strict gate; preserve the interrupted queue and successful resume result.

For each publisher record, cross-check source-version year, volume and DOI against the actual PDF header as well as its URL and locator. A copied version template caused eight ALEA cover errors at checkpoint500; originals were correct, but affected items were quarantined until covers and receipts were rebuilt. The validator now rejects conflicting explicitly stated version/locator DOIs. This guard supplements, rather than replaces, the original-header check.

## Lessons from checkpoints 1400–1600

- In addition to statement and proof pages, verify every declared PDF context page is a positive integer, within the unchanged source PDF, and actually included in the wrapper. The live gate enforces this. Missing notation pages are a material context defect even when the theorem proof is intact.
- INDEX display fields cannot contain literal pipes or newlines. Rephrase only editorial titles (for example “absolute value less than one”); do not alter source mathematics. Import preflight must fail before copying or activation. Rebuild the same reserved ID after a correction, never count it twice.
- For a legitimate original-paper-plus-corrigendum bundle, retain both original files, official license evidence, exact page concatenation history and hashes. Keep primary DOI identity distinct from secondary component identities. Bind component paths through extra_source_paths so compilation receipts cover them; do not disable the DOI guard.
- A PDF parser warning requires diagnosis, not automatic acceptance or automatic rejection. Determine whether the affected object is a mathematical content/font/image resource or an unused/broken link destination. Inspect all relevant selected pages and record the finding. Never rewrite source bytes to silence a warning.
- A named standard hypothesis with an obvious inconsistent printed display may only support an explicitly scoped source-faithful item when the authored proof unambiguously uses that named hypothesis or a stated prerequisite. Preserve the display and warning. If accepting requires choosing a new bound, reconstructing an argument, or fixing an ambiguous core formula, hold the candidate.
- Root-owned finalized-block ceilings control intake. Do not consume a collector's progressive ready list; wait for explicit completion of the entire source block. Keep source dates as actual acquisition dates rather than copying a milestone date.
- Every milestone backup must be restored to a fresh directory and independently validated. A completed upload alone is not recovery evidence. Direct streaming multipart packaging requires all project writers paused; its per-file manifest is not a whole-ZIP hash.

A primary proof can be present but its packet still omit the author's substantive nearby construction on which that proof depends. The early native context audit identified this in ten packets; each was quarantined before context repair. Distinguish standard named foundations from the local new construction. Expand only with exact authored support, preserve original IDs and primary hashes, and record any bounded ancillary omissions. If a supporting theorem's hypotheses do not cover the selected statement (for example integral versus general schemes), keep the item held rather than silently generalizing the support. This is materials closure, not an independent mathematical referee or a demand to reproduce every textbook prerequisite.

When scanning journal volumes in ascending year order, first check later official volume indexes or correction records for errata to selected papers. Preserve a bounded correction ledger with exact target article and affected theorem scope. JEP157 changed JEP133's numerical conclusion before that pending item entered a checkpoint; JEP206 and272 explicitly affected other results, so unrelated selected claims were not automatically discarded. Bind any used erratum as a separate unchanged, licensed source component. If the erratum introduces another unresolved quantitative inconsistency, hold the item rather than reconstructing a corrected proof to meet a quota.
