# Incremental maintenance and bounded difficulty note — 2026-10-15

Fixed source: `51fd50e2c4bcb59ff26648da58ae580c67c9ff85`. Comparison baseline: `d6606aed2c59c18b3beb393b6488c8a0a8396a76`. This report belongs to draft PR #3; it changes no production records, qualifications, stable IDs, proof text, or controller state.

## Metadata and navigation

The complete fixed manifest contains **22,526 material records**: 14,875 legacy and 7,651 prepared. Prepared splits into 7,648 author-material-collection records and 3 records labeled current; legacy includes 9 labeled current. Those 12 current labels are preserved metadata, not a fresh qualification audit or proof of new-standard admission. No new qualified-production count is inferred.

Relative to the existing reading-index snapshot: **1,938 additions, zero removals, and all 20,588 old records unchanged field-for-field**. Stable ID, item-path and nonempty exact claim-key scans found no new collision involving an added record. This is identity metadata checking, not a semantic uniqueness certificate.

The unchanged PR #2 renderer accepted the complete new manifest, including stable IDs, numeric aliases, distinct item paths, safe link syntax and source URLs; in-memory output has 113 pages plus its entry page. This is a compatibility check, not a published index refresh. PR #2 remains explicitly bound to its prior snapshot. Original compact INDEX and all production files were untouched. Existing generator test evidence was reused; no proof compilation or production test suite was repeated.

Limits: this pass did not resolve all new package paths against the complete remote Git tree, restore SQLite, verify all upstream URLs, or rerun a whole-library semantic assessment. The selected source and delivered TeX below were actually read at the fixed revision. No claim of a full path-validation pass is made.

## Source concentration, with works separate from channels

The existing [source metadata helper](../2026-10-14/source_metadata_statistics.py) was reused unchanged. Chapters and versions of Stacks, Open Logic and HoTT are grouped as one work each. DOI/arXiv aliases are unioned only when explicitly linked in a manifest row. No title similarity matching is used.

The 1,938 additions normalize to four work identifiers:
- Stacks Project: 1,804 (93.085655%)
- Open Logic Project: 85
- HoTT book: 42
- DOI 10.5802/ahl.16: 7

Across all 7,651 prepared records, the same method gives 72 normalized work identifiers; Stacks contributes 6,884 (89.975167%). These are metadata-normalized identifiers, not independently verified distinct works. Unresolved grouping rows are zero for these two subsets, but unrecorded DOI/arXiv equivalences and attribution conflicts may remain. The known 900000403 attribution issue and all earlier assessed records are unchanged, not silently corrected.

Retrieval channels among additions are separately counted by source_url host: stacks.math.columbia.edu 1,472; github.com 417; homotopytypetheory.org 42; ahl.centre-mersenne.org 7. Multiple channels, chapters, tags or mirrors do not increase the work count. The new material volume therefore adds substantially less source diversity than its row count suggests. No quota or production schema change is proposed.

## Targeted difficulty risk: stable ID 900005753

Selection was purposeful: this new record explicitly justifies H2 by a “sequential citation assembly.” It is not a random sample and supports no population-wide pass/fail rate.

Identity: task X1-sp-simplicial-fppf-glue-neg-ext-zero, revision r001; claim stacks:spaces-simplicial.tex:lemma-fppf-glue-neg-ext-zero. This note does not modify the recorded H2.

Evidence:
- [Full delivered statement](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/51fd50e2c4bcb59ff26648da58ae580c67c9ff85/editable-corpus/prepared-jobs/X1-sp-simplicial-fppf-glue-neg-ext-zero/r001/package-root-r001/items/L46303_author_proof.tex#L257-L274) specifies an fppf hypercovering, gluing data and negative self-Ext vanishing.
- [Allowed premises and editorial disclosure](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/51fd50e2c4bcb59ff26648da58ae580c67c9ff85/editable-corpus/prepared-jobs/X1-sp-simplicial-fppf-glue-neg-ext-zero/r001/package-root-r001/items/L46303_author_proof.tex#L242-L256) explicitly supply the Cartesian-system construction, realization of that system as an object, and unbounded fppf cohomological descent.
- [Entire delivered main proof](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/51fd50e2c4bcb59ff26648da58ae580c67c9ff85/editable-corpus/prepared-jobs/X1-sp-simplicial-fppf-glue-neg-ext-zero/r001/package-root-r001/items/L46303_author_proof.tex#L276-L288) applies those three premises in sequence: build the system; obtain K'; descend K' to K.
- [Pinned author main statement and proof](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/51fd50e2c4bcb59ff26648da58ae580c67c9ff85/editable-corpus/prepared-jobs/X1-sp-simplicial-fppf-glue-neg-ext-zero/r001/package-root-r001/sources/L46303/source-01.tex#L7878-L7909) agree with the counted statement/proof.
- [Source Cartesian-system construction](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/51fd50e2c4bcb59ff26648da58ae580c67c9ff85/editable-corpus/prepared-jobs/X1-sp-simplicial-fppf-glue-neg-ext-zero/r001/package-root-r001/sources/L46303/source-01.tex#L3401-L3445) contains a displayed construction and explicitly omits the cocycle-composition verification. The delivery already discloses this; this report neither fills it in nor treats the author result as false.
- [Realization input](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/51fd50e2c4bcb59ff26648da58ae580c67c9ff85/editable-corpus/prepared-jobs/X1-sp-simplicial-fppf-glue-neg-ext-zero/r001/package-root-r001/sources/L46303/source-01.tex#L3538-L3570) and [descent input](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/51fd50e2c4bcb59ff26648da58ae580c67c9ff85/editable-corpus/prepared-jobs/X1-sp-simplicial-fppf-glue-neg-ext-zero/r001/package-root-r001/sources/L46303/source-01.tex#L7675-L7795) carry the substantive supporting mechanisms in the original work.

Auxiliary conclusion: **strict H2 is not established by the recorded “three sequential citations” rationale alone under the delivered allowed-premise list**. Once these three strong inputs are granted, the remaining counted proof is their composition; no additional substantial construction or estimate is identified in that main proof. The specialized setting does require background, so this is a conservative boundary/insufficient-evidence judgment, not a declaration that the original theorem is elementary or incorrect. Confidence is high about the stated remaining proof obligations and moderate about difficulty classification without a standardized learner baseline.

The ordinary doctoral-qualifying-exam level is used only as a broad anchor for independent proof obligations; no unusually specialized qualifying exam is imposed as the threshold. Terminology, theorem prestige, source length and successful compilation are not used as difficulty proxies. If later admission instead requires proving the source-local inputs, the task has a different allowed-premise scope and must be assessed on that scope with complete author material. This note does not retroactively change it.

Overlap: shared source-local inputs do not prove duplicate claims. No semantic duplicate or deletion recommendation is made without comparing complete independent target claims and their substantive proof obligations. Earlier overlap cases and stable recovery chains remain unchanged.

## Reproduction and boundaries

Read both fixed manifests, key records by the unchanged problem_id, and compare full records. Run the existing renderer's render(manifest, snapshot) in memory. For source grouping, use the unchanged helper's alias_map(explicit_aliases(all_rows)) and summary(subset, aliases), with additions selected by stable ID set difference. The adjacent source-summary.json records the resulting metadata aggregates.

This is a bounded maintenance finding for the existing draft review, not a replacement intake gate, mathematical correctness certification, new audit platform, or instruction to another production line. No deletion, H change, qualification change, merge to main, or production ownership change was performed.
