# JEP338 Proposition 4.5: author material only

One whole simultaneous extension claim; no count for support lemmas, theorem components, source files or revision. Task GPDOT261014-MD-0008 r002, problem_id null. r001 parent compilation exposed a wrapper macro omission; r002 restores the exact native macro and is pending parent reassembly/compilation. See TECHNICAL_NOTE_r002.md.

## Fixed source and license

Adam Keilthy and Martin Raum, *Formal deformations of modular forms and multiple L-values*, JEP 13 (2026), 853–890, published 2026-04-30. DOI 10.5802/jep.338; arXiv2404.03519 is an alias only, not a mixed version.

- Publisher: https://jep.centre-mersenne.org/articles/10.5802/jep.338/
- Official PDF: https://jep.centre-mersenne.org/item/10.5802/jep.338.pdf
- Official native TeX: https://jep.centre-mersenne.org/article/10.5802/jep.338/file/src/tex/JEP_2026__13__853_0.tex
- License: CC BY4.0, explicit publisher metadata preserved in license-extract.txt and license-evidence.json; full publisher HTML saved privately outside upload whitelist.

## Material coverage

Full Proposition4.5 statement 1764–1774; full proof1776–1875 and full Lemma4.6 1879–1906, printed882–884 / PDF30–32. Retain native sections1,2.1–2.2,3.1–3.3, BCH setup3.4 through native1460, and4.2 through Lemma4.6. This includes all original first-order/formal setup, Prop2.7 weight-transport proof, Lemma2.8 vanishing proof, Cor3.1, Theorem3.12 lifting proof, and Theorem4.3 existence proof. BCH setup and Lie cocycle/section definitions at1427–1460 were added after directly inspecting dependencies. All counted proof and current support are author text, not generated substitutes. Two native TikZ commutative diagrams in §1 are retained; no external figure assets are needed.

Full bibliography recovered from the official HTML (all31 entries, original numeric citation labels and native keys). Precise external tools are distinguished in task.standard_prerequisites. Bol's identity has no independent source bibliography item; its actual third-derivative formula is retained and no reference was invented. Brown's §4.3 motivic construction is not a dependency. The two non-load-bearing forward/context pointers to §2.3 and Cor4.7 have explicit original locators.

H2: recursive multivariable BCH coefficient isolation, lower-degree Lie-polynomial cancellation establishing a third-derivative cocycle, cohomological obstruction solution and integration, then equivariant transport to weight k. The full construction remains in the counted proof; section existence alone does not replace it. No H3/correctness certification.

## Saved identity comparison and limitation

Saved complete identities: both full main manifests, refreshed current-main identity with 398 additions through commit 652c73d739c2d5f85ef9e56e2b14e93310b2e024, saved deltas, worklists/occupancy and five-line in-flight records, plus all 26 prior canonical own tasks. Zero exact DOI/arXiv/title matches in saved scan. In-flight cutoff 2026-10-14T17:36:45Z; later in-flight overlap remains unconfirmed. No final global-unique admission.

- main150424 / arxiv2311.14438:lemmaepsan1: Locally analytic p-adic differential-operator action/interpolation of Gauss-Manin connection on nearly overconvergent modular forms; different scalar field, object and conclusion from the simultaneous complex formal cocycle-section extension.
- CP13-AG-055-padic-Gauss-Manin-interpolation: Same p-adic Gauss-Manin work, main theorem at native lines 222–237; no recursive complex modular-deformation pair extension.
- main192985 / arxiv2601.12860:thm-7: Rankin–Cohen operation on vector-valued/Jacobi modular forms rather than recursive construction of a formal deformation and compatible section.
- GPDOT261014-PM-0011 and PM-0014: Perfectoid torsors and G-zips respectively; different spaces, hypotheses and claims. No source-identity overlap.

## Presentation and publication boundary

The task declares an exact public_dependency_paths whitelist. Original author TeX/PDF and license notice remain intact. The presentation uses a standard article wrapper and original math macros; no cedram/journal class, style, logo assets or third-party package files are distributed. Original “formal deformation cycle”, homology wording, superscripts and indexing are not mathematically repaired. Bibliography and counter changes are only presentation recovery. Source notices are recorded in task.json. Full author PDF is evidence, never a substitute for editable text.

Private identity snapshots, publisher HTML, preparation helper and validation result are excluded from public dependencies. No assembly, TeX run, QA, SQLite, Git, server/controller changes or formal IDs performed here. Saved-scope material completeness is not final global uniqueness or admission.
