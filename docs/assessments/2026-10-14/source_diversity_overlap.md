# Source diversity and overlap assessment — 2026-10-14

[Assessment navigation](README.md) · [Difficulty assessment overview](difficulty_assessment_overview.md)

This auxiliary assessment describes metadata and carries forward bounded overlap evidence at snapshot `41b4ab870b5b24d235c74e7123bccba6d9b9b042`. It is an independent assessment for maintenance, not a formal human content review. It changes no material, review state, deduplication decision, H2/H3 qualification, or qualification count. Its population is the material rows in the [fixed-snapshot manifest](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/manifest.json), not the older published index or a count of independently verified mathematical problems.

There are **19,789 material rows = 14,875 legacy + 4,914 prepared**. The manifest records `review_state=current` for nine legacy rows and three prepared rows (12 rows total); **4,911 prepared rows** retain `author_material_collection`. Preparation, a recorded source version, or `unique_within_reviewed_scope` does not establish current qualification or uniqueness across the whole corpus.

## Population and identifier normalization

All material-share percentages use the full stratum denominator: all = 19,789, legacy = 14,875, prepared = 4,914. Distinct identifiers are deduplicated within each stratum and cannot be added across strata.

| Measure | All | Legacy | Prepared |
| --- | --- | --- | --- |
| Material rows | 19,789 | 14,875 | 4,914 |
| Exact raw `source_id` strings | 14,644 | 14,514 | 197 |
| Normalized work identifiers | 14,472 | 14,470 | 70 |
| Rows without resolved normalized identifier | 0 | 0 | 0 |

Normalization strips arXiv version suffixes, lowercases DOI identifiers, and collapses publisher mirrors of the same DOI. DOI from `source_id` takes precedence over a download-URL suffix: row `3198` uses DOI `10.5802/afst.1805`, and its `afst.1805.pdf` URL is a PDF locator, not a second work. Stacks Project, the HoTT book, Open Logic Project, and AlJabr-2 each count as one work identifier, despite multiple chapters or statement rows.

The manifest explicitly associates a DOI `source_id` and arXiv `source_url` in the same row for **32 legacy rows representing 29 distinct alias pairs**. These explicit identities are unioned, with the DOI label preferred. No title matching or inferred cross-registry identity is used; unlinked DOI/arXiv aliases remain unresolved as bibliographic equivalence. The 14,472 normalized identifiers are **not 14,472 certified independently distinct works**. Zero unresolved identifier rows means every row receives an identifier under these rules, not that work independence is certified. The union implies 67 shared exact raw identifiers and 68 shared normalized identifiers across legacy and prepared strata; these remain identifier overlaps.

## Retrieval platform and source-family shares

These categories describe retrieval platforms, source projects, journal families, or DOI prefixes. They are not mathematical disciplines. A DOI-prefix category alone does not establish a publisher or venue independently of its metadata. Counts and percentages measure material-row shares, not journals, authors, chapters, or unique claims.

| Platform / source family | All: n / 19,789 (%) | Legacy: n / 14,875 (%) | Prepared: n / 4,914 (%) |
| --- | --- | --- | --- |
| arXiv | 13,880 (70.1400%) | 13,697 (92.0807%) | 183 (3.7241%) |
| Stacks Project | 4,656 (23.5282%) | 359 (2.4134%) | 4,297 (87.4440%) |
| SIGMA | 320 (1.6171%) | 256 (1.7210%) | 64 (1.3024%) |
| Centre-Mersenne/jep | 255 (1.2886%) | 174 (1.1697%) | 81 (1.6484%) |
| Centre-Mersenne/alco | 203 (1.0258%) | 183 (1.2303%) | 20 (0.4070%) |
| HoTT book | 133 (0.6721%) | 0 (0.0000%) | 133 (2.7066%) |
| Open Logic Project | 123 (0.6216%) | 0 (0.0000%) | 123 (2.5031%) |
| Centre-Mersenne/ahl | 90 (0.4548%) | 77 (0.5176%) | 13 (0.2646%) |
| DOI 10.4086 | 55 (0.2779%) | 55 (0.3697%) | 0 (0.0000%) |
| DOI 10.19086 | 43 (0.2173%) | 43 (0.2891%) | 0 (0.0000%) |
| DOI 10.58997 | 22 (0.1112%) | 22 (0.1479%) | 0 (0.0000%) |
| AlJabr-2 | 3 (0.0152%) | 3 (0.0202%) | 0 (0.0000%) |
| DOI 10.46298 | 2 (0.0101%) | 2 (0.0134%) | 0 (0.0000%) |
| Centre-Mersenne/afst | 1 (0.0051%) | 1 (0.0067%) | 0 (0.0000%) |
| DOI 10.1017 | 1 (0.0051%) | 1 (0.0067%) | 0 (0.0000%) |
| DOI 10.14231 | 1 (0.0051%) | 1 (0.0067%) | 0 (0.0000%) |
| DOI 10.4171 | 1 (0.0051%) | 1 (0.0067%) | 0 (0.0000%) |

Legacy is dominated by arXiv (13,697 / 14,875 = 92.0807%). Prepared is dominated by the single Stacks Project work identifier (4,297 / 4,914 = 87.4440%). A large material total therefore does not by itself establish breadth of independently sourced works or disciplines.

## Work concentration

For each stratum, rank normalized identifiers by material-row count. Top-k sums the first k counts and divides by the full stratum's material total. Equal-count ties use deterministic identifier order. This does not measure statement duplication or proof equivalence.

| Concentration | All | Legacy | Prepared |
| --- | --- | --- | --- |
| Top 1 | 4,656 / 19,789 (23.5282%) | 359 / 14,875 (2.4134%) | 4,297 / 4,914 (87.4440%) |
| Top 5 | 4,960 / 19,789 (25.0644%) | 372 / 14,875 (2.5008%) | 4,599 / 4,914 (93.5897%) |
| Top 10 | 5,050 / 19,789 (25.5192%) | 383 / 14,875 (2.5748%) | 4,684 / 4,914 (95.3195%) |

Each entry below is a normalized identifier and material-row count; its percentage uses the complete stratum, not the top-ten subtotal. Source chapters are not separate works.

| Rank | All identifier | All n (%) | Legacy identifier | Legacy n (%) | Prepared identifier | Prepared n (%) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `work:Stacks-Project` | 4,656 (23.5282%) | `work:Stacks-Project` | 359 (2.4134%) | `work:Stacks-Project` | 4,297 (87.4440%) |
| 2 | `work:HoTT-book` | 133 (0.6721%) | `doi:10.4086/toc.2024.v020a001` | 4 (0.0269%) | `work:HoTT-book` | 133 (2.7066%) |
| 3 | `work:OpenLogic` | 123 (0.6216%) | `doi:10.19086/da.143834` | 3 (0.0202%) | `work:OpenLogic` | 123 (2.5031%) |
| 4 | `arxiv:2402.11616` | 24 (0.1213%) | `doi:10.5802/alco.345` | 3 (0.0202%) | `arxiv:2402.11616` | 23 (0.4681%) |
| 5 | `arxiv:2411.13723` | 24 (0.1213%) | `doi:10.5802/alco.447` | 3 (0.0202%) | `arxiv:2411.13723` | 23 (0.4681%) |
| 6 | `doi:10.5802/alco.351` | 20 (0.1011%) | `work:AlJabr-2` | 3 (0.0202%) | `doi:10.5802/alco.351` | 19 (0.3867%) |
| 7 | `doi:10.3842/sigma.2015.034` | 18 (0.0910%) | `doi:10.19086/da.124610` | 2 (0.0134%) | `doi:10.3842/sigma.2015.034` | 17 (0.3460%) |
| 8 | `doi:10.5802/jep.317` | 18 (0.0910%) | `doi:10.19086/da.138191` | 2 (0.0134%) | `doi:10.5802/jep.317` | 17 (0.3460%) |
| 9 | `arxiv:2305.07126` | 17 (0.0859%) | `doi:10.19086/da.143451` | 2 (0.0134%) | `arxiv:2305.07126` | 16 (0.3256%) |
| 10 | `arxiv:2404.14020` | 17 (0.0859%) | `doi:10.19086/da.144015` | 2 (0.0134%) | `arxiv:2404.14020` | 16 (0.3256%) |

## Stacks claim-tag coverage

Only an explicit `primary.tag_url` counts as a known tag for the primary counted claim. A tag in `source_url` is a source-entry locator; other strings may contain context or cross-reference tags. These do not establish the primary claim tag.

| Stacks tag measure | All | Legacy | Prepared |
| --- | --- | --- | --- |
| Stacks material rows | 4,656 | 359 | 4,297 |
| Rows with explicit primary claim tag | 359 | 359 | 0 |
| Distinct explicit primary claim tags | 359 | 359 | 0 |
| Primary claim tag unknown | 4,297 | 0 | 4,297 |
| Rows with source-entry URL tag | 1,700 | 0 | 1,700 |
| Distinct source-entry URL tags | 41 | 0 | 41 |

The legacy stratum has 359 / 359 Stacks rows with 359 distinct explicit primary tags. **All 4,297 prepared Stacks rows have unknown primary tags** under this definition. The 359 known primary tags cover 359 / 4,656 = 7.7105% of all Stacks rows. Prepared `source_url` entry tags appear in 1,700 rows but identify only 41 distinct entry tags. They cannot be substituted for 1,700 distinct primary claims.

The broader all-string scan records 7,061 tag references / 2,648 distinct tag strings in all Stacks rows; legacy has 5,246 / 2,515 and prepared 1,815 / 156. These auxiliary reference counts are **not main-claim tags**, distinct statements, or works.

## Author and year coverage

`author` is a descriptive credit string, often containing multiple people or a collective. Exact-string uniqueness is affected by punctuation, spelling, formatting, aliases, collective names, and errors. It is not a people count. Explicit `authors` arrays also include collective credits and the known erroneous value for `900000403`.

| Measure | All | Legacy | Prepared |
| --- | --- | --- | --- |
| Rows with nonempty `author` | 19,789 / 19,789 (100.0000%) | 14,875 / 14,875 (100.0000%) | 4,914 / 4,914 (100.0000%) |
| Distinct exact `author` credit strings | 12,871 | 12,868 | 69 |
| Rows with explicit `authors` array | 4,914 / 19,789 (24.8320%) | 0 / 14,875 (0.0000%) | 4,914 / 4,914 (100.0000%) |
| Distinct explicit `authors` credit strings | 147 | 0 | 147 |
| Rows with structured publication year | 0 / 19,789 (0.0000%) | 0 / 14,875 (0.0000%) | 0 / 4,914 (0.0000%) |
| Rows with arXiv identifier-year proxy | 13,880 / 19,789 (70.1400%) | 13,697 / 14,875 (92.0807%) | 183 / 4,914 (3.7241%) |

The 12,871 / 12,868 / 69 exact credit strings and 147 explicit list strings measure recorded-credit diversity, not distinct authors. Legacy has no explicit `authors` arrays. Person-level author diversity remains unknown without identity resolution and correction of conflicts.

There is no structured publication-year field: coverage is 0 / 19,789 all, 0 / 14,875 legacy, and 0 / 4,914 prepared. An arXiv identifier year is only an identifier/deposit-era proxy, **not a publication year**. It excludes non-arXiv sources. No publication year is inferred from retrieval dates, local snapshots, source-version prose, or TeX dates. Rows without this proxy number 5,909 all, 1,178 legacy, and 4,731 prepared.

The following proxy distribution uses counts; observable denominators are 13,880 arXiv rows all, 13,697 legacy, and 183 prepared.

| arXiv identifier year (proxy) | All / 13,880 | Legacy / 13,697 | Prepared / 183 |
| --- | --- | --- | --- |
| 2007 | 1 | 1 | 0 |
| 2008 | 1 | 1 | 0 |
| 2010 | 1 | 1 | 0 |
| 2013 | 2 | 2 | 0 |
| 2015 | 2 | 2 | 0 |
| 2016 | 3 | 3 | 0 |
| 2017 | 7 | 7 | 0 |
| 2018 | 9 | 9 | 0 |
| 2019 | 15 | 15 | 0 |
| 2020 | 29 | 29 | 0 |
| 2021 | 123 | 115 | 8 |
| 2022 | 251 | 228 | 23 |
| 2023 | 506 | 469 | 37 |
| 2024 | 1241 | 1130 | 111 |
| 2025 | 4135 | 4131 | 4 |
| 2026 | 7554 | 7554 | 0 |

## Conflicting attribution metadata: 900000403

The [official JEP article page](https://jep.centre-mersenne.org/articles/10.5802/jep.177/) identifies *The Markov-quantile process attached to a family of marginals* by **Charles Boubel and Nicolas Juillet**, DOI `10.5802/jep.177`, under **CC BY 4.0**. This prior official-page check is reused here.

The manifest's `author` string (`Charles Boubel; Nicolas Juillet`), work, source URL, DOI, and `license` (`CC BY4.0`) identify that JEP article correctly. Its `authors` array instead contains `The Univalent Foundations Program`. Packaged provenance incorrectly carries the HoTT author, work, URL, and CC BY-SA 3.0 Unported license; the item TeX author/date headers also carry the incorrect HoTT attribution/license. License evidence correctly records CC BY 4.0 and the JEP DOI. These are conflicting metadata layers, not evidence for a second mathematical source.

This report classifies the row from the manifest DOI as Centre-Mersenne/jep. Correcting only its `authors` list to the two JEP authors leaves 147 distinct explicit credit strings, family/work counts, and Top 1/5/10 concentration unchanged because those credits occur elsewhere already. Classification from the incorrect provenance title would spuriously move a row to HoTT. **No production metadata is silently corrected here.**

## Eleven bounded overlap cases

The evidence levels preserve previous checks; this report performs no new whole-proof reading, compilation, scientific correctness verification, or corpus-wide deduplication audit. Source-version wording such as “exact bytes pinned by SHA256” is a copied raw field, **not a new digest check**. Recorded labels, review states, and deduplication states are not independent endorsements.

| Evidence level | Pairs | Interpretation |
| --- | --- | --- |
| Prior complete primary + proof whitespace-normalized text match | 3 | Earlier bounded text comparison; retained, no deletion. |
| Prior primary statement text match; full proof unresolved | 4 | Primary text checked earlier; proof equivalence unresolved. |
| Same-source-location metadata candidate | 2 | Matching metadata locators; no text comparison. |
| Different-chapter same-label risk case | 2 | Different chapter and locators; not same-source duplicate evidence. |

For `900001188 / 900004094` and `900001194 / 900004126`, `morphisms.tex` and `stacks-morphisms.tex` are different chapters. The `stacks-` prefix is meaningful; earlier normalization removed it and wrongly produced same-source candidates. These two PR2 candidates are corrected **in this report**, without editing PR2 or the corpus records. Shared labels across those chapters are collision risks, not duplicate findings.

Every record below retains its stable material ID, raw source ID/version, claim key, item path, and every primary/proof span with label. Item links point to actual packaged TeX in the fixed Git tree. Original `primary.path` and `proof_spans.path` values are **logical source locators**, not asserted repository-root Git paths. For each locator, the packaged-source link is resolved by the row's `source_files.original_path → source_files.path` mapping; only these mapped paths are linked. Scoped fixed-tree path checks establish link targets, not digest validity or text equivalence. Line spans refer to source locators, not generated item TeX. Some version strings retain inherited encoding artifacts verbatim.

### 1. 900000014 / 900000479

**Evidence:** Prior primary statement text checked; full proof equivalence unresolved

**Material `900000014`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/items/900000014_author_proof.tex)

- `source_id`: `arxiv:2411.13723v3`
- Raw `source_version`: arXiv:2411.13723v3 (CC BY 4.0)
- Raw `claim_key`: `arxiv:2411.13723:Feb_23_2024_2`
- `item_path`: `prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/items/900000014_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/free-steiner-model-theory-2411.13723v3/source0.tex`, lines **740–741**; label: Feb_23_2024_2. Mapped packaged source: [prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex).

Proof spans:

- Original path `sources/free-steiner-endomorphisms-2412.06055v3/source0.tex`, lines **287–298**; label: author proof of unconfined iff HF-orderable. Mapped packaged source: [prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-01.tex).

- Original path `sources/free-steiner-model-theory-2411.13723v3/source0.tex`, lines **650–660**; label: restriction of an HF-order to an intersection. Mapped packaged source: [prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex).

- Original path `sources/free-steiner-model-theory-2411.13723v3/source0.tex`, lines **701–717**; label: bounded strongness transitivity and one-point product extension. Mapped packaged source: [prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex).

- Original path `sources/free-steiner-model-theory-2411.13723v3/source0.tex`, lines **742–749**; label: complete identification-and-free-amalgam construction. Mapped packaged source: [prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/B-logic-steiner-quantitative-amalgamation/r002/package-root-r002/sources/900000014/source-00.tex).

**Material `900000479`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-logic-fsts-n-amalgamation/r002/package-root-r002/items/L764_author_proof.tex)

- `source_id`: `arxiv:2411.13723v3`
- Raw `source_version`: arXiv:2411.13723v3 (CC BY 4.0)
- Raw `claim_key`: `arxiv:2411.13723v3:Feb_23_2024_2`
- `item_path`: `prepared-jobs/LIT-logic-fsts-n-amalgamation/r002/package-root-r002/items/L764_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/free-steiner-model-theory-2411.13723v3/source0.tex`, lines **740–741**; label: prop Feb_23_2024_2 (statement, author label). Mapped packaged source: [prepared-jobs/LIT-logic-fsts-n-amalgamation/r002/package-root-r002/sources/L764/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-logic-fsts-n-amalgamation/r002/package-root-r002/sources/L764/source-00.tex).

Proof spans:

- Original path `sources/free-steiner-model-theory-2411.13723v3/source0.tex`, lines **742–749**; label: the complete author proof of the labelled proposition, retained line for line. Mapped packaged source: [prepared-jobs/LIT-logic-fsts-n-amalgamation/r002/package-root-r002/sources/L764/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-logic-fsts-n-amalgamation/r002/package-root-r002/sources/L764/source-00.tex).

### 2. 900000026 / 900000466

**Evidence:** Prior primary statement text checked; full proof equivalence unresolved

**Material `900000026`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/items/900000026_author_proof.tex)

- `source_id`: `doi:10.5802/jep.353`
- Raw `source_version`: Journal de l’École polytechnique — Mathématiques 13 (2026), publisher version, DOI 10.5802/jep.353
- Raw `claim_key`: `doi:10.5802/jep.353:argumentprinciplelemma`
- `item_path`: `prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/items/900000026_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/hartree-phase-mixing-jep-2026-353/source0.tex`, lines **1139–1146**; label: boundary half-line conditions imply uniform Penrose stability. Mapped packaged source: [prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex).

Proof spans:

- Original path `sources/hartree-phase-mixing-jep-2026-353/source0.tex`, lines **1036–1056**; label: full directional weighted Fourier-integral estimate. Mapped packaged source: [prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex).

- Original path `sources/hartree-phase-mixing-jep-2026-353/source0.tex`, lines **1092–1131**; label: full uniform response boundedness and decay proofs. Mapped packaged source: [prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex).

- Original path `sources/hartree-phase-mixing-jep-2026-353/source0.tex`, lines **1147–1189**; label: argument-principle proof and low-frequency compactification. Mapped packaged source: [prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/C-analysis-uniform-penrose-boundary-criterion/r002/package-root-r002/sources/900000026/source-01.tex).

**Material `900000466`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-analysis-hartree-argument-principle/r001/package-root-r001/items/L754_author_proof.tex)

- `source_id`: `doi:10.5802/jep.353`
- Raw `source_version`: Journal de l’École polytechnique — Mathématiques 13 (2026), publisher version, DOI 10.5802/jep.353
- Raw `claim_key`: `doi:10.5802/jep.353:lemma-argumentprinciplelemma`
- `item_path`: `prepared-jobs/LIT-analysis-hartree-argument-principle/r001/package-root-r001/items/L754_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/hartree-phase-mixing-jep-2026-353/source0.tex`, lines **1139–1146**; label: lemma argumentprinciplelemma (statement, author label). Mapped packaged source: [prepared-jobs/LIT-analysis-hartree-argument-principle/r001/package-root-r001/sources/L754/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-analysis-hartree-argument-principle/r001/package-root-r001/sources/L754/source-01.tex).

Proof spans:

- Original path `sources/hartree-phase-mixing-jep-2026-353/source0.tex`, lines **1147–1189**; label: the complete author proof of the labelled lemma, retained line for line. Mapped packaged source: [prepared-jobs/LIT-analysis-hartree-argument-principle/r001/package-root-r001/sources/L754/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/LIT-analysis-hartree-argument-principle/r001/package-root-r001/sources/L754/source-01.tex).

### 3. 900000168 / 900002616

**Evidence:** Prior primary statement text checked; full proof equivalence unresolved

**Material `900000168`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-alg-demazure-presentation/r001/package-root-r001/items/DSH-alg-demazure-presentation_author_proof.tex)

- `source_id`: `doi:10.3842/SIGMA.2014.110`
- Raw `source_version`: Official SIGMA 10 (2014) article 110, DOI 10.3842/SIGMA.2014.110; journal PDF and native TeX acquired 2026-10-01, exact bytes pinned by SHA256
- Raw `claim_key`: `doi:10.3842/SIGMA.2014.110:prop-WvsD`
- `item_path`: `prepared-jobs/DSH-alg-demazure-presentation/r001/package-root-r001/items/DSH-alg-demazure-presentation_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **396–425**; label: Proposition, source label WvsD (statement lines 396-425). Mapped packaged source: [prepared-jobs/DSH-alg-demazure-presentation/r001/package-root-r001/sources/DSH-alg-demazure-presentation/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-alg-demazure-presentation/r001/package-root-r001/sources/DSH-alg-demazure-presentation/source-01.tex).

Proof spans:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **426–442**; label: the author's own proof immediately following the proposition (lines 426-442). Mapped packaged source: [prepared-jobs/DSH-alg-demazure-presentation/r001/package-root-r001/sources/DSH-alg-demazure-presentation/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-alg-demazure-presentation/r001/package-root-r001/sources/DSH-alg-demazure-presentation/source-01.tex).

**Material `900002616`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-sigma110-WvsD/r002/package-root-r002/items/L40139_author_proof.tex)

- `source_id`: `doi:10.3842/SIGMA.2014.110`
- Raw `source_version`: Official SIGMA 10 (2014) article 110, DOI 10.3842/SIGMA.2014.110; journal PDF and native TeX acquired 2026-10-01, exact bytes pinned by SHA256
- Raw `claim_key`: `sigma-2014-110-demazure-fusion:WvsD`
- `item_path`: `prepared-jobs/P1-sigma110-WvsD/r002/package-root-r002/items/L40139_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **396–425**; label: author proposition environment, source label WvsD (statement, source lines 396-425, with the author's displayed defining relations inside the span). Mapped packaged source: [prepared-jobs/P1-sigma110-WvsD/r002/package-root-r002/sources/L40139/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-sigma110-WvsD/r002/package-root-r002/sources/L40139/source-01.tex).

Proof spans:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **426–442**; label: the author's own proof environment immediately following the statement (source lines 426-442). Mapped packaged source: [prepared-jobs/P1-sigma110-WvsD/r002/package-root-r002/sources/L40139/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-sigma110-WvsD/r002/package-root-r002/sources/L40139/source-01.tex).

### 4. 900000169 / 900002494

**Evidence:** Prior primary statement text checked; full proof equivalence unresolved

**Material `900000169`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-alg-demazure-shifted-vec/r001/package-root-r001/items/DSH-alg-demazure-shifted-vec_author_proof.tex)

- `source_id`: `doi:10.3842/SIGMA.2014.110`
- Raw `source_version`: Official SIGMA 10 (2014) article 110, DOI 10.3842/SIGMA.2014.110; journal PDF and native TeX acquired 2026-10-01, exact bytes pinned by SHA256
- Raw `claim_key`: `doi:10.3842/SIGMA.2014.110:lemma-crucial`
- `item_path`: `prepared-jobs/DSH-alg-demazure-shifted-vec/r001/package-root-r001/items/DSH-alg-demazure-shifted-vec_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **454–467**; label: Lemma, source label crucial, all three relations (statement lines 454-467). Mapped packaged source: [prepared-jobs/DSH-alg-demazure-shifted-vec/r001/package-root-r001/sources/DSH-alg-demazure-shifted-vec/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-alg-demazure-shifted-vec/r001/package-root-r001/sources/DSH-alg-demazure-shifted-vec/source-01.tex).

Proof spans:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **468–493**; label: the author's own proof immediately following the lemma (lines 468-493). Mapped packaged source: [prepared-jobs/DSH-alg-demazure-shifted-vec/r001/package-root-r001/sources/DSH-alg-demazure-shifted-vec/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/DSH-alg-demazure-shifted-vec/r001/package-root-r001/sources/DSH-alg-demazure-shifted-vec/source-01.tex).

**Material `900002494`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-sigma110-crucial/r001/package-root-r001/items/L40137_author_proof.tex)

- `source_id`: `doi:10.3842/SIGMA.2014.110`
- Raw `source_version`: Official SIGMA 10 (2014) article 110, DOI 10.3842/SIGMA.2014.110; journal PDF and native TeX acquired 2026-10-01, exact bytes pinned by SHA256
- Raw `claim_key`: `sigma-2014-110-demazure-fusion:crucial`
- `item_path`: `prepared-jobs/P1-sigma110-crucial/r001/package-root-r001/items/L40137_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **454–467**; label: author lemma environment, source label crucial (statement, source lines 454-467, with the author's three numbered relations inside the span). Mapped packaged source: [prepared-jobs/P1-sigma110-crucial/r001/package-root-r001/sources/L40137/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-sigma110-crucial/r001/package-root-r001/sources/L40137/source-01.tex).

Proof spans:

- Original path `sources/sigma-2014-110-demazure-fusion/pinned-original-source.tex`, lines **468–493**; label: the author's own proof environment immediately following the statement (source lines 468-493). Mapped packaged source: [prepared-jobs/P1-sigma110-crucial/r001/package-root-r001/sources/L40137/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-sigma110-crucial/r001/package-root-r001/sources/L40137/source-01.tex).

### 5. 900000181 / 900002048

**Evidence:** Prior complete primary+proof whitespace-normalized text match; retained, no deletion

**Material `900000181`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-logic-shore-blocking-wf/r001/package-root-r001/items/L402_author_proof.tex)

- `source_id`: `arxiv:2402.11616v3`
- Raw `source_version`: arXiv:2402.11616v3 (CC BY 4.0)
- Raw `claim_key`: `arxiv:2402.11616v3:lem:shore-blocking-wf`
- `item_path`: `prepared-jobs/ACL-logic-shore-blocking-wf/r001/package-root-r001/items/L402_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/logic-fl02-conservation-of-ramsey-s-theorem-f/pinned-original-source.tex`, lines **426–431**; label: lemma lem:shore-blocking-wf, the counted statement. Mapped packaged source: [prepared-jobs/ACL-logic-shore-blocking-wf/r001/package-root-r001/sources/L402/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-logic-shore-blocking-wf/r001/package-root-r001/sources/L402/source-00.tex).

Proof spans:

- Original path `sources/logic-fl02-conservation-of-ramsey-s-theorem-f/pinned-original-source.tex`, lines **433–450**; label: the author proof environment that immediately follows the counted statement. Mapped packaged source: [prepared-jobs/ACL-logic-shore-blocking-wf/r001/package-root-r001/sources/L402/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-logic-shore-blocking-wf/r001/package-root-r001/sources/L402/source-00.tex).

**Material `900002048`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P2-logic-shore-blocking-wf/r001/package-root-r001/items/L38002_author_proof.tex)

- `source_id`: `arxiv:2402.11616v3`
- Raw `source_version`: arXiv:2402.11616v3 (CC BY 4.0)
- Raw `claim_key`: `arxiv:2402.11616:lem:shore-blocking-wf`
- `item_path`: `prepared-jobs/P2-logic-shore-blocking-wf/r001/package-root-r001/items/L38002_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/logic-fl02-conservation-of-ramsey-s-theorem-f/pinned-original-source.tex`, lines **426–431**; label: lemma lem:shore-blocking-wf (statement). Mapped packaged source: [prepared-jobs/P2-logic-shore-blocking-wf/r001/package-root-r001/sources/L38002/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P2-logic-shore-blocking-wf/r001/package-root-r001/sources/L38002/source-01.tex).

Proof spans:

- Original path `sources/logic-fl02-conservation-of-ramsey-s-theorem-f/pinned-original-source.tex`, lines **433–450**; label: author proof environment immediately following the statement of lem:shore-blocking-wf. Mapped packaged source: [prepared-jobs/P2-logic-shore-blocking-wf/r001/package-root-r001/sources/L38002/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P2-logic-shore-blocking-wf/r001/package-root-r001/sources/L38002/source-01.tex).

### 6. 900000913 / 900000914

**Evidence:** Prior complete primary+proof whitespace-normalized text match; retained, no deletion

**Material `900000913`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-morph-nr-branches-lemma/r001/package-root-r001/items/L1467_author_proof.tex)

- `source_id`: `stacks-project:more-morphisms.tex:local-snapshot-20261011`
- Raw `source_version`: Stacks Project source tree, file more-morphisms.tex, corpus local snapshot 20261011
- Raw `claim_key`: `stacks:stacks-more-morphisms:lemma-nr-branches`
- `item_path`: `prepared-jobs/S3-morph-nr-branches-lemma/r001/package-root-r001/items/L1467_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-more-morphisms/pinned-original-source.tex`, lines **10333–10352**; label: lemma-nr-branches. Mapped packaged source: [prepared-jobs/S3-morph-nr-branches-lemma/r001/package-root-r001/sources/L1467/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-morph-nr-branches-lemma/r001/package-root-r001/sources/L1467/source-02.tex).

Proof spans:

- Original path `sources/stacks-more-morphisms/pinned-original-source.tex`, lines **10354–10402**; label: complete author proof of lemma-nr-branches. Mapped packaged source: [prepared-jobs/S3-morph-nr-branches-lemma/r001/package-root-r001/sources/L1467/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-morph-nr-branches-lemma/r001/package-root-r001/sources/L1467/source-02.tex).

**Material `900000914`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-morph-nr-branches/r001/package-root-r001/items/L1436_author_proof.tex)

- `source_id`: `stacks-project:more-morphisms.tex:local-snapshot-20261011`
- Raw `source_version`: Stacks Project source tree, file more-morphisms.tex, corpus local snapshot 20261011
- Raw `claim_key`: `stacks:stacks-more-morphisms.tex:lemma-nr-branches`
- `item_path`: `prepared-jobs/S3-morph-nr-branches/r001/package-root-r001/items/L1436_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-more-morphisms/pinned-original-source.tex`, lines **10333–10352**; label: lemma-nr-branches. Mapped packaged source: [prepared-jobs/S3-morph-nr-branches/r001/package-root-r001/sources/L1436/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-morph-nr-branches/r001/package-root-r001/sources/L1436/source-02.tex).

Proof spans:

- Original path `sources/stacks-more-morphisms/pinned-original-source.tex`, lines **10354–10402**; label: complete author proof of lemma-nr-branches. Mapped packaged source: [prepared-jobs/S3-morph-nr-branches/r001/package-root-r001/sources/L1436/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-morph-nr-branches/r001/package-root-r001/sources/L1436/source-02.tex).

### 7. 900001279 / 900003671

**Evidence:** Prior complete primary+proof whitespace-normalized text match; retained, no deletion

**Material `900001279`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-spaces-univ-thickening-unramified-2/r001/package-root-r001/items/L1473_author_proof.tex)

- `source_id`: `stacks-project:spaces-more-morphisms.tex:local-snapshot-20261011`
- Raw `source_version`: Stacks Project source tree, file spaces-more-morphisms.tex, corpus local snapshot 20261011
- Raw `claim_key`: `stacks:stacks-spaces-more-morphisms:lemma-universal-thickening-unramified`
- `item_path`: `prepared-jobs/S3-spaces-univ-thickening-unramified-2/r001/package-root-r001/items/L1473_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-spaces-more-morphisms/pinned-original-source.tex`, lines **3184–3190**; label: lemma-universal-thickening-unramified. Mapped packaged source: [prepared-jobs/S3-spaces-univ-thickening-unramified-2/r001/package-root-r001/sources/L1473/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-spaces-univ-thickening-unramified-2/r001/package-root-r001/sources/L1473/source-02.tex).

Proof spans:

- Original path `sources/stacks-spaces-more-morphisms/pinned-original-source.tex`, lines **3192–3215**; label: complete author proof of lemma-universal-thickening-unramified. Mapped packaged source: [prepared-jobs/S3-spaces-univ-thickening-unramified-2/r001/package-root-r001/sources/L1473/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-spaces-univ-thickening-unramified-2/r001/package-root-r001/sources/L1473/source-02.tex).

**Material `900003671`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-spaces-universal-thickening-unramified/r001/package-root-r001/items/L16217_author_proof.tex)

- `source_id`: `stacks-project:spaces-more-morphisms.tex:local-snapshot-20261011`
- Raw `source_version`: Stacks Project source tree, file spaces-more-morphisms.tex, corpus local snapshot 20261011
- Raw `claim_key`: `stacks:stacks-spaces-more-morphisms.tex:lemma-universal-thickening-unramified`
- `item_path`: `prepared-jobs/S3-spaces-universal-thickening-unramified/r001/package-root-r001/items/L16217_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-spaces-more-morphisms/pinned-original-source.tex`, lines **3184–3190**; label: lemma-universal-thickening-unramified. Mapped packaged source: [prepared-jobs/S3-spaces-universal-thickening-unramified/r001/package-root-r001/sources/L16217/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-spaces-universal-thickening-unramified/r001/package-root-r001/sources/L16217/source-02.tex).

Proof spans:

- Original path `sources/stacks-spaces-more-morphisms/pinned-original-source.tex`, lines **3192–3215**; label: complete author proof of lemma-universal-thickening-unramified. Mapped packaged source: [prepared-jobs/S3-spaces-universal-thickening-unramified/r001/package-root-r001/sources/L16217/source-02.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S3-spaces-universal-thickening-unramified/r001/package-root-r001/sources/L16217/source-02.tex).

### 8. 900000052 / 900004162

**Evidence:** Metadata-only normalization candidate; no text comparison

**Material `900000052`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-cohomology-graded-boundary-mittag-leffler/r001/package-root-r001/items/900000052_author_proof.tex)

- `source_id`: `stacks-project:cohomology.tex:local-snapshot-20261011`
- Raw `source_version`: Stacks Project local source snapshot captured 2026-10-11; upstream commit not recorded
- Raw `claim_key`: `stacks:cohomology:lemma-ML-general`
- `item_path`: `prepared-jobs/ACL-cohomology-graded-boundary-mittag-leffler/r001/package-root-r001/items/900000052_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `focused-seeds/ACL/sources/stacks-snapshot-20261011/cohomology.tex`, lines **8930–8949**; label: lemma-ML-general. Mapped packaged source: [prepared-jobs/ACL-cohomology-graded-boundary-mittag-leffler/r001/package-root-r001/sources/900000052/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-cohomology-graded-boundary-mittag-leffler/r001/package-root-r001/sources/900000052/source-01.tex).

Proof spans:

- Original path `focused-seeds/ACL/sources/stacks-snapshot-20261011/cohomology.tex`, lines **8951–8986**; label: full author graded-boundary proof. Mapped packaged source: [prepared-jobs/ACL-cohomology-graded-boundary-mittag-leffler/r001/package-root-r001/sources/900000052/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-cohomology-graded-boundary-mittag-leffler/r001/package-root-r001/sources/900000052/source-01.tex).

**Material `900004162`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S11-csh-ML-general/r001/package-root-r001/items/L30130_author_proof.tex)

- `source_id`: `stacks-project:cohomology.tex:local-snapshot-20261011`
- Raw `source_version`: Stacks Project local source snapshot captured 2026-10-11; upstream commit not recorded
- Raw `claim_key`: `stacks:cohomology.tex:lemma-ML-general`
- `item_path`: `prepared-jobs/S11-csh-ML-general/r001/package-root-r001/items/L30130_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-cohomology/pinned-original-source.tex`, lines **8930–8949**; label: author Lemma environment, source label lemma-ML-general (statement, source lines 8930-8949). Mapped packaged source: [prepared-jobs/S11-csh-ML-general/r001/package-root-r001/sources/L30130/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S11-csh-ML-general/r001/package-root-r001/sources/L30130/source-01.tex).

Proof spans:

- Original path `sources/stacks-cohomology/pinned-original-source.tex`, lines **8951–8986**; label: the author's own proof environment immediately following the lemma (source lines 8951-8986). Mapped packaged source: [prepared-jobs/S11-csh-ML-general/r001/package-root-r001/sources/L30130/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S11-csh-ML-general/r001/package-root-r001/sources/L30130/source-01.tex).

### 9. 900000167 / 900004626

**Evidence:** Metadata-only normalization candidate; no text comparison

**Material `900000167`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-logic-uniform-thin-arrays/r001/package-root-r001/items/ACL-logic-uniform-thin-arrays_author_proof.tex)

- `source_id`: `arxiv:2412.11598v3`
- Raw `source_version`: arXiv:2412.11598v3 (CC BY 4.0)
- Raw `claim_key`: `arxiv:2412.11598v3:lem:arrays`
- `item_path`: `prepared-jobs/ACL-logic-uniform-thin-arrays/r001/package-root-r001/items/ACL-logic-uniform-thin-arrays_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/logic-fl05-ramsey-like-theorems-for-the-schre/pinned-original-source.tex`, lines **683–685**; label: lemma lem:arrays (statement). Mapped packaged source: [prepared-jobs/ACL-logic-uniform-thin-arrays/r001/package-root-r001/sources/ACL-logic-uniform-thin-arrays/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-logic-uniform-thin-arrays/r001/package-root-r001/sources/ACL-logic-uniform-thin-arrays/source-00.tex).

Proof spans:

- Original path `sources/logic-fl05-ramsey-like-theorems-for-the-schre/pinned-original-source.tex`, lines **687–697**; label: immediate author proof of lem:arrays. Mapped packaged source: [prepared-jobs/ACL-logic-uniform-thin-arrays/r001/package-root-r001/sources/ACL-logic-uniform-thin-arrays/source-00.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/ACL-logic-uniform-thin-arrays/r001/package-root-r001/sources/ACL-logic-uniform-thin-arrays/source-00.tex).

**Material `900004626`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P2-fl05-arrays/r001/package-root-r001/items/L38049_author_proof.tex)

- `source_id`: `arxiv:2412.11598v3`
- Raw `source_version`: arXiv:2412.11598v3 (CC BY 4.0)
- Raw `claim_key`: `arxiv:2412.11598:lem:arrays`
- `item_path`: `prepared-jobs/P2-fl05-arrays/r001/package-root-r001/items/L38049_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/logic-fl05-ramsey-like-theorems-for-the-schre/pinned-original-source.tex`, lines **683–685**; label: author Lemma environment, source label lem:arrays (statement, source lines 683-685). Mapped packaged source: [prepared-jobs/P2-fl05-arrays/r001/package-root-r001/sources/L38049/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P2-fl05-arrays/r001/package-root-r001/sources/L38049/source-01.tex).

Proof spans:

- Original path `sources/logic-fl05-ramsey-like-theorems-for-the-schre/pinned-original-source.tex`, lines **687–697**; label: the author's proof environment of lem:arrays (source lines 687-697), the explicit colouring driven by a uniform modulus and the three-step thinning analysis. Mapped packaged source: [prepared-jobs/P2-fl05-arrays/r001/package-root-r001/sources/L38049/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P2-fl05-arrays/r001/package-root-r001/sources/L38049/source-01.tex).

### 10. 900001188 / 900004094

**Evidence:** Metadata same-label risk case across different chapters morphisms.tex and stacks-morphisms.tex, different locators. Prior normalization improperly removed a meaningful chapter prefix; not same-source duplicate evidence. No text comparison.

**Material `900001188`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S13-morph-point-finite-type/r002/package-root-r002/items/L4025_author_proof.tex)

- `source_id`: `stacks-project:morphisms.tex:local-snapshot-20261012`
- Raw `source_version`: Stacks Project source tree, file morphisms.tex, corpus local snapshot 20261012
- Raw `claim_key`: `stacks:morphisms.tex:lemma-point-finite-type`
- `item_path`: `prepared-jobs/S13-morph-point-finite-type/r002/package-root-r002/items/L4025_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-morphisms/pinned-original-source.tex`, lines **2826–2840**; label: author Lemma environment, source label lemma-point-finite-type, statement, source lines 2826-2840. Mapped packaged source: [prepared-jobs/S13-morph-point-finite-type/r002/package-root-r002/sources/L4025/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S13-morph-point-finite-type/r002/package-root-r002/sources/L4025/source-01.tex).

Proof spans:

- Original path `sources/stacks-morphisms/pinned-original-source.tex`, lines **2842–2875**; label: the author's own proof environment immediately following the statement, source lines 2842-2875. Mapped packaged source: [prepared-jobs/S13-morph-point-finite-type/r002/package-root-r002/sources/L4025/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S13-morph-point-finite-type/r002/package-root-r002/sources/L4025/source-01.tex).

**Material `900004094`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-asm-point-finite-type/r001/package-root-r001/items/L40253_author_proof.tex)

- `source_id`: `stacks-project:stacks-morphisms.tex:local-snapshot-20261012`
- Raw `source_version`: Stacks Project git a04446e57ec1 (2026-07-28); file stacks-morphisms.tex; corpus local snapshot 20261012
- Raw `claim_key`: `stacks:stacks-morphisms.tex:lemma-point-finite-type`
- `item_path`: `prepared-jobs/P1-asm-point-finite-type/r001/package-root-r001/items/L40253_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-algebraic-stacks-morphisms/pinned-original-source.tex`, lines **3655–3665**; label: author lemma environment, source label lemma-point-finite-type (statement, source lines 3655-3665). Mapped packaged source: [prepared-jobs/P1-asm-point-finite-type/r001/package-root-r001/sources/L40253/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-asm-point-finite-type/r001/package-root-r001/sources/L40253/source-01.tex).

Proof spans:

- Original path `sources/stacks-algebraic-stacks-morphisms/pinned-original-source.tex`, lines **3667–3694**; label: the author's own proof environment immediately following the statement (source lines 3667-3694). Mapped packaged source: [prepared-jobs/P1-asm-point-finite-type/r001/package-root-r001/sources/L40253/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-asm-point-finite-type/r001/package-root-r001/sources/L40253/source-01.tex).

### 11. 900001194 / 900004126

**Evidence:** Metadata same-label risk case across different chapters morphisms.tex and stacks-morphisms.tex, different locators. Prior normalization improperly removed a meaningful chapter prefix; not same-source duplicate evidence. No text comparison.

**Material `900001194`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S13-morph-universally-injective-characterize/r002/package-root-r002/items/L4016_author_proof.tex)

- `source_id`: `stacks-project:morphisms.tex:local-snapshot-20261012`
- Raw `source_version`: Stacks Project source tree, file morphisms.tex, corpus local snapshot 20261012
- Raw `claim_key`: `stacks:morphisms.tex:lemma-universally-injective`
- `item_path`: `prepared-jobs/S13-morph-universally-injective-characterize/r002/package-root-r002/items/L4016_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-morphisms/pinned-original-source.tex`, lines **1577–1593**; label: author Lemma environment, source label lemma-universally-injective, statement, source lines 1577-1593. Mapped packaged source: [prepared-jobs/S13-morph-universally-injective-characterize/r002/package-root-r002/sources/L4016/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S13-morph-universally-injective-characterize/r002/package-root-r002/sources/L4016/source-01.tex).

Proof spans:

- Original path `sources/stacks-morphisms/pinned-original-source.tex`, lines **1595–1667**; label: the author's own proof environment immediately following the statement, source lines 1595-1667. Mapped packaged source: [prepared-jobs/S13-morph-universally-injective-characterize/r002/package-root-r002/sources/L4016/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/S13-morph-universally-injective-characterize/r002/package-root-r002/sources/L4016/source-01.tex).

**Material `900004126`** — [fixed packaged item TeX](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-asm-universally-injective/r001/package-root-r001/items/L40190_author_proof.tex)

- `source_id`: `stacks-project:stacks-morphisms.tex:local-snapshot-20261012`
- Raw `source_version`: Stacks Project git a04446e57ec1 (2026-07-28); file stacks-morphisms.tex; corpus local snapshot 20261012
- Raw `claim_key`: `stacks:stacks-morphisms.tex:lemma-universally-injective`
- `item_path`: `prepared-jobs/P1-asm-universally-injective/r001/package-root-r001/items/L40190_author_proof.tex`
- Recorded `review_state`: `author_material_collection`; recorded `dedup_state`: `unique_within_reviewed_scope`

Primary locator:

- Original path `sources/stacks-algebraic-stacks-morphisms/pinned-original-source.tex`, lines **2906–2920**; label: author lemma environment, source label lemma-universally-injective (statement, source lines 2906-2920). Mapped packaged source: [prepared-jobs/P1-asm-universally-injective/r001/package-root-r001/sources/L40190/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-asm-universally-injective/r001/package-root-r001/sources/L40190/source-01.tex).

Proof spans:

- Original path `sources/stacks-algebraic-stacks-morphisms/pinned-original-source.tex`, lines **2922–2974**; label: the author's own proof environment immediately following the statement (source lines 2922-2974). Mapped packaged source: [prepared-jobs/P1-asm-universally-injective/r001/package-root-r001/sources/L40190/source-01.tex](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/prepared-jobs/P1-asm-universally-injective/r001/package-root-r001/sources/L40190/source-01.tex).

## Reproduction and limits

Run from the repository root with Python 3:

```sh
python3 docs/assessments/2026-10-14/source_metadata_statistics.py --repo . --snapshot 41b4ab870b5b24d235c74e7123bccba6d9b9b042
python3 -m unittest discover -s docs/assessments/2026-10-14 -p test_source_metadata_statistics.py -v
```

The helper reads metadata without writing scores, changing schemas, merging/deleting materials, updating qualification, or proving bibliographic independence. Its small tests check normalization and metadata semantics. These commands are supplied for reproduction; this document alone does not certify a test run or repeat prior text comparisons. Final maintenance validation is recorded with the maintenance review evidence.

The supplied fixed-snapshot statistics and eleven-pair evidence are this report's basis. Unknowns remain: unlinked DOI/arXiv aliases, independent work identities, person-level authors, publication years, prepared Stacks primary claim tags, proof equivalence in four statement-only cases, and text overlap in metadata-only cases. Eleven bounded cases cannot estimate a corpus-wide duplication rate. Source-family shares cannot establish discipline diversity, and source concentration alone does not establish redundancy or difficulty.
