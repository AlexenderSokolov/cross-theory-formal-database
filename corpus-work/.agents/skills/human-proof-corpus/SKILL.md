---
name: human-proof-corpus
description: Use when collecting, admitting, validating, or recovering source-grounded mathematical problems with human-authored proofs in this corpus project.
---

# Human-proof corpus

Count only active items passing the evidence gate. File counts, source tags, H-level labels, and historical success notes are not qualification. The tools verify evidence and compilation; they do not certify mathematics or difficulty.

## Source screening

- Read the exact statement and every consecutive author proof in a pinned source revision. Match title, hypotheses, conclusion and claimed difficulty to that statement. A research chapter can contain elementary exercises; write a concrete above-ordinary-PhD-qual difficulty reason rather than labeling every extracted theorem advanced.
- Preserve author mathematics. Keep exact source excerpts, hashes, line ranges, author, version, retrieval date and license. Never invent source title, tag, locator or theorem attribution.
- Investigate “Omitted,” “left to the reader,” and missing proof environments. Reject omitted core reasoning. Only use an explicitly authorized bounded omitted-detail exception after recording why the omitted detail is ancillary and the substantive author proof remains complete. Preserve the author's omission wording.
- Close local context: include referenced assumptions, equations, situation introductions and required adjacent statements; preserve ordinary external prerequisites as references. Keep each context's raw-file hash, exact line interval and excerpt hash. Check semantic uniqueness against existing claims, including different tags for equivalent results.

## Current workflow

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
python3 scripts/validate_corpus.py --item ID
python3 scripts/validate_corpus.py
```

On failure, keep the item quarantined and remove its active INDEX row; preserve artifacts and explain the reason. Do not use old build PDFs or merely mark review booleans true to meet a target. Final qualified count comes from validation_report.json, not INDEX labels or highest ID.

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
