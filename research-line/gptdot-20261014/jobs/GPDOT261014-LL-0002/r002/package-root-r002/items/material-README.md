# GPDOT261014-LL-0002 — frozen author-proof material

## Delivery state

- Task: `task.json`, revision `r001`, schema 2, `problem_id: null`, `material_only: true`
- Origin class: `human_authored_proof_assistant_transcription`; the formal proof is fixed author Lean source, with Lean/Lake/kernel checking unrun by this collector
- One H2 material candidate, combining the author's A3, B3-small and B3-large cases of weak-to-full graded Steinberg relation implication
- Material state: `candidate_pending_inflight_dedup`; frozen for the parent to complete full in-flight semantic dedup and XeLaTeX assembly/compilation
- No final uniqueness, net-new count, public problem ID, admission or upload is claimed
- The real `prepared_delivery.py` locator helpers were used, and all declared spans/assets exist. Its unchanged final material validation currently stops with `semantic uniqueness decision and scope required`, because the dedup conclusion is deliberately pending
- No Lean, Lake, kernel check, XeLaTeX compilation, database/job/index/status operation or Git operation was performed

## Fixed identity and licenses

Paper: Eric Wang, Arohee Bhoja, Cayden Codel and Noah G. Singer, *Algebra Is Half the Battle: Verifying Presentations of Graded Unipotent Chevalley Groups*, ITP 2025, LIPIcs 352, 9:1–9:19, published 2025-09-22

- DOI: `10.4230/LIPIcs.ITP.2025.9`
- URN: `urn:nbn:de:0030-drops-246071`
- Official record: <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2025.9>
- Official author code: <https://github.com/singerng/steinberg-formalization>
- Fixed author code commit: `e02f0aaba4b045f5c1eadfe9078a3027a3b52d68`
- Official fixed archive directory: `swh:1:dir:dcac1d58f554132e469a8339afb6224cb72562db`
- Official archive revision anchor: `swh:1:rev:e02f0aaba4b045f5c1eadfe9078a3027a3b52d68`
- Fixed commit metadata names the same Git tree object as the official SWH directory. This is source-version identification; no new hash was computed
- Verified package alias: <https://reservoir.lean-lang.org/%40singerng/steinberg>
- Verified title variant: *Algebra is half the battle: Verifying presentations for graded unipotent Chevalley groups*
- The initially supplied `github.com/singergn/steinberg-formalization` returned 404. It is a spelling discrepancy, not a verified source alias
- No arXiv alias of this formalization paper was identified

The article/PDF/HTML are CC BY 4.0. The fixed author source code is Apache-2.0. `license-evidence.json` gives separate evidence. The complete Apache license, copyright notices and author README are retained under `sources/code-e02f0aa/`. Only selection and source-code presentation were prepared here; no mathematical source was rewritten or supplemented

## Exact counted claim and proof scope

The counted scope is the exact author's relation-implication declarations below, collected as one main result. Article Theorem 1 is context. The article's presentation-isomorphism commentary, matrix realizations and HDX consequences are not separately claimed or counted

| Case and exact declaration | Native module | Full target and proof range | Native hypotheses |
| --- | --- | --- | --- |
| `Steinberg.A3.full_relations_implied_by_weak_relations` | `Steinberg/A3/Thm.lean` | 384–444 | arbitrary `Ring R` |
| `Steinberg.B3Small.full_relations_implied_by_weak_relations` | `Steinberg/B3Small/Thm.lean` | 518–588 | `Field F`, `(2 : F) ≠ 0` |
| `Steinberg.B3Large.full_relations_implied_by_weak_relations` | `Steinberg/B3Large/Thm.lean` | 572–691 | `Field F`, `(2 : F) ≠ 0`, every field element is a sum of two squares |

All 26 locally imported author proof/definition/macro modules are reproduced completely in `proof_spans`: 8,276 native source lines. This preserves the missing-root relation derivations, local presented-group/free-group support, graded transport, nonhomogeneous lifting, degree reflection, B3-large staged root establishment and actual author macro implementation. These local proof-core constructions are not relabeled as background prerequisites

`source-map.json` identifies exact native paths/lines, presentation paths/lines, local import order and external imports. There are no missing local imports in the selected targets' closure. The unselected author's whole project is not represented as a runnable build. External standard Lean/mathlib packages are referenced by the author's fixed toolchain and manifest rather than recopied

The proof spans are full editable code text, not screenshots or external links. They can populate the later database `proof_text` in full. Companion assets retain the selected `.lean` files, license, README, `lean-toolchain`, `lakefile.lean` and `lake-manifest.json`

Author toolchain: `leanprover/lean4:v4.15.0-rc1`. Fixed mathlib revision: `a988e8b369e20ae90b4998923e4efcd732a1da62`. Source collection and a placeholder scan do not establish kernel acceptance or mathematical correctness. Neither is claimed

## Difficulty

H2 is supported by the independent non-routine relation-sufficiency core: bootstrapping missing-root relations from restricted weak relations, nonhomogeneous lifting, degree reflection and graded transport, and the staged B3-large root construction using explicit field hypotheses. The three cases, mechanical rewrites and helper results are not counted separately. No H3 claim is made

## Parent checks still pending

- Parent reports complete public-main metadata at `dba879f`, 20,464 items, with no identity match for this paper DOI, `2411.05916`, `10.4230/LIPIcs.ICALP.2021.84` or `steinberg-formalization`
- Parent identified 17 broad Chevalley and 23 broad Steinberg word neighbors; lexical overlap alone does not establish duplicate identity. Complete in-flight identity snapshots have arrived; the CCC2022.18 directed source comparison is documented in `dedup-neighbor-CCC2022-18.md/json`. The parent retains the final overall semantic conclusion
- Original mathematical source neighbors are O'Donnell–Singer, `arXiv:2411.05916` / `10.48550/arXiv.2411.05916` (B3), and Kaufman–Oppenheim, `10.4230/LIPIcs.ICALP.2021.84` (A3). They are not aliases of this formalization paper. An alternate formal proof cannot justify a new count if the same claim is already present
- `assembly.engine` is `xelatex`, `allow_shell_escape` is false. The wrapper displays complete code with native module line numbers and an explicit guide to the three final proof locations
- Installed font character maps were inspected: Noto Sans Mono covers the code except `⦃⦄⬝`. The wrapper applies glyph-only DejaVu Sans fallback for `⦃⦄` and Noto Sans Symbols2 for `⬝`, keeping original Unicode code points. This wrapper has not yet been compiled or visually checked
- No known source-material or permission gap remains for the selected author-code relation-implication scope. Final dedup and parent compilation are outstanding gates

## Files

- `task.json`: exact real-interface task/span/assembly record
- `source-map.json`: source-version, dependency and line-location map
- `license-evidence.json`: article/code license evidence
- `presentation/`: faithful editable statement/context and full code proof TeX
- `sources/conference-2025/`: fixed official PDF/HTML
- `sources/code-e02f0aa/`: selected complete native code and author metadata
- `.work/`: acquisition and preparation cache, outside selected delivery assets

## Directed CCC2022.18 comparison update

`dedup-neighbor-CCC2022-18.md/json` records the complete main and closest source-core comparison against CP01A1332F-GA-072. Its Prop50 graded normal form assumes full Steinberg relations, whereas this task establishes all full relations inside the specified restricted weak quotient. The authored obligations are distinct in this focused comparison; proof-medium replacement is not used as a new-count reason. Full parent-scope dedup and compilation remain pending. Neighbor raw assets stay in `.work`
