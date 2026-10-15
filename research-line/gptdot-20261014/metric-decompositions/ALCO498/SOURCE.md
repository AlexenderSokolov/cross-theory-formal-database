# ALCO498: one principal author result

## Ready material

- Task: `GPDOT261014-MD-0006`, revision `r001`; no formal problem ID
- Counted result: Flynn–Ramos–Young, published Theorem 3.7, all three parts, printed p.983
- Current support retained in the same task: complete intrinsic FI-arrangement construction on p.981, Proposition 3.5 and its complete proof on pp.981–982
- Status: frozen material; existing `prepared_delivery.validate_record(task, [], material_only=True)` and `validate_task` pass. Awaiting parent assembly/compilation and fresh in-flight check. No compiled, database, uploaded or production-main increment is claimed

## Exact source and license

Ian Flynn, Eric Ramos and Benjamin Young, *Representation Stability in the Intrinsic Hyperplane Arrangements Associated to Irreducible Representations of the Symmetric Groups*, Algebraic Combinatorics 9 (2026), no.4, 973–992, published online 2026-09-02, DOI `10.5802/alco.498`, journal item `ALCO_2026__9_4_973_0`.

- Official landing page: https://alco.centre-mersenne.org/articles/10.5802/alco.498/
- Actual published PDF: https://alco.centre-mersenne.org/item/10.5802/alco.498.pdf
- Original retrieved PDF: `sources/published.pdf`, 21 physical pages including the license cover, 20 printed article pages
- Official metadata page retained as `sources/published.html`
- License: CC BY 4.0. The PDF cover explicitly prints the copyright, license and license URL. The official metadata page lines 1073–1077 independently identifies CC-BY 4.0 and retained author copyright
- License terms: https://creativecommons.org/licenses/by/4.0/

The editable mathematical text is mechanically transcribed from this published PDF only. The source PDF is retained unchanged. No author mathematical statements, proofs, or assumptions are generated or repaired.

## Official editable-source check

The retrieved ALCO498 landing page's available full-text block (lines 733–748) exposes the PDF link only. Its complete links were checked for TeX, XML/JATS and supplementary full-text source; there is no such link. The page contains metadata, abstract and bibliography rather than complete mathematical article HTML. Exact DOI/title searches found the official article and author publication/code pages, but no verified official full published editable text.

A journal-native endpoint pattern was supplied by the parent after that pattern successfully retrieved another assigned ALCO article. The corresponding ALCO498 request was actually made:

`https://alco.centre-mersenne.org/article/10.5802/alco.498/file/src/tex/ALCO_2026__9_4_973_0.tex`

It returned **HTTP 404 Not Found** on 2026-10-15, with no request left running. This is a bounded failed-source check, not a claim that every conceivable official source is unavailable. The allowed faithful published-PDF route supplies the complete selected proof without that source.

## Explicit arXiv distinction

The same-work identity is arXiv `2405.13291`, DOI `10.48550/arXiv.2405.13291`. Both fixed v1 and v2 use the arXiv non-exclusive distribution license, not CC BY. The material worker directly inspected v1's actual license link; the parent supplied its direct v2 verification. V1's identity/license page is retained privately at `.work/arxiv-v1.html`. No arXiv proof text, native TeX or image was used in this extraction or made a public dependency. The journal license is not applied to arXiv materials.

## Exact extraction and completeness

`published-extract.tex` contains source-location comments and exact original numerical labels. `SPANS.json` and `task.json` give real file/line intervals and roles.

- Partitions, Young diagrams and tabloid realization: Definition 2.1 and Remarks 2.2–2.3, pp.976–977
- Padded modules and FI definitions: Theorem 2.5, Definitions 2.6–2.7 and Theorem 2.8, pp.977–978
- Intrinsic hyperplanes and complement: Definition 2.10 plus its well-definedness/action discussion, pp.978–979; complete Definition 2.12, pp.979–980
- Arrangement morphisms, finite generation and normality: Definition 3.1 and Remark 3.2, p.980
- Gadish's standard input: original Theorem 3.4, p.981
- Current construction: all text from “Our way forward has therefore been made clear” through the introduction of Proposition 3.5, p.981
- Current substantive support: complete Proposition 3.5 and its proof, pp.981–982
- Principal claim and proof: complete Theorem 3.7 and proof, p.983
- Author method qualification: complete Remark 3.8, p.983
- Cited bibliography: original entries [2], [4], [9], [15], [19], [23], p.991, with numbering retained

Original p.976 is physical PDF p.5; p.983 is physical p.12; p.991 is physical p.20. The license cover and all selected mathematical/bibliographic physical pages were rendered and visually inspected. The selection does not depend on a figure. The diagrams in unselected Remark 3.6 concern continuity rather than the selected normality/stability proof and are not referenced by its proof.

The source uses both `p` and `p_V` in the final dimension sentences of Theorems 2.8 and 3.7. These are preserved as printed, with no mathematical correction. The source's cokernel terminology and other wording are also preserved without interpretation or correction.

## Difficulty and counting

One H2 principal claim is proposed. Its retained nonroutine work is the representation-to-arrangement construction and the normality proof: the author analyzes the tabloid map and cokernel support, relates containment in intrinsic hyperplanes to partition labels and normal vectors, and lifts the corresponding flats. These specific current obligations remain in the task after admitting the standard FI-module, Gadish and Orlik–Solomon inputs. The bounded character/partition conclusions and the quotient caveat then remain in the full Theorem 3.7 proof. Terminology, venue and the mere act of invoking a stability theorem are not the difficulty basis.

Proposition 3.5, Theorem 1.1, the background theorems and definitions are not separate counted materials. No alternate arXiv version is counted.

## Identity and scope

`DEDUP-NOTES.json` preserves the parent's supplied exact DOI/title/arXiv identity search at 2026-10-15 01:18–01:19 UTC across the complete main-manifest-95b49064 snapshot, 398 current-main changed/additional identities, all supplied identities-20261014 JSONLs and FIVE_LINE_GLOBAL_IDENTITY_DELTA. No exact same-work hit was reported.

The worker supplemented only the actual journal-item alias `ALCO_2026__9_4_973_0` and targeted intrinsic-hyperplane/FI-arrangement claim-neighbor terms over those supplied files. No hit occurred. This does not assert exhaustive semantic equivalence search. The parent owns the final fresh in-flight check before upload.

## Delivery boundary

All public inputs are enumerated in `task.json`. `.work/` is private/excluded. It contains rendering/extraction witnesses, the v1 license-only page and the material-writing helper; it is not a native proof source. No jobs, compile output, SQLite, Git, production queue, owner, lock, or shared-control file was changed by this material worker. Final TeX/PDF presentation verification remains with the parent's authorized compiler.
