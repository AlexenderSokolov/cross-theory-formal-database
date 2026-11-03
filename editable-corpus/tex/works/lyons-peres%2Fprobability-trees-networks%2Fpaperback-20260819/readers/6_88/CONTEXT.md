# Exercise 6.88 and its Author Comment — reader context

Source work: *Probability on Trees and Networks*, Russell Lyons and Yuval Peres.
Fixed source version: author paperback version 2026-08-19 (716 physical pages,
21,010,205 bytes), `original/book_pb.pdf`.

Page convention throughout this reader: `physical = printed + 17`.
The exercise statement is on physical p. 252 (printed p. 235); the author
Comment is on physical p. 638 (printed p. 621). Section 6.9, which the exercise
names and which defines the constants it uses, opens on physical p. 233
(printed p. 216); the anchored expansion constants are defined on physical
p. 234 (printed p. 217); the random subdivision, the exponential tail and
Exercise 6.23 are on physical p. 238 (printed p. 221); the notation of equation
(6.33), used by the definition of `\Phi^{**}_{\E}`, is on physical p. 217
(printed p. 200); the constant `\Phi^{**}_{\E}` and Theorem 6.50 are also on
physical p. 238; the remark that cites this exercise is on physical p. 240
(printed p. 223).

## What is in the reader

| span | lines | content |
| --- | --- | --- |
| context | 19–118 | source/scope statement, errata statement, ten literal-feature items, the note on where the number 6.88 occurs in the body, Section 6.9, the anchored expansion constants, the random subdivision and the exponential tail, the notation of (6.33), `\Phi^{**}_{\E}` with the tree equality and Theorem 6.50, and the necessity remark with the Galton–Watson corroboration |
| `\clearpage` | 120 | page break so the primary statement starts a page |
| primary statement | 121–127 | Exercise 6.88 verbatim, standing alone as the whole of the exercise |
| primary proof | 129–146 | the complete author Comment on Exercise 6.88 verbatim, including its three displays and the two-line approximation |
| editorial note | 148–149 | what the reader does not claim: the Comment's first equivalence is asserted, not derived, and the two normalizations are not identified |

## Uncounted context carried in the reader

The exercise is not self-contained, so six passages are reprinted as context and
are not counted as part of the primary statement or the primary proof:

- Section 6.9, Anchored Expansion and Percolation, from its heading through the
  two conjectures and the attribution to Benjamini, Lyons and Schramm (1999),
  physical p. 233 (printed p. 216);
- the anchored expansion constants `\Phi^{*}_{\E}(G)` and `\Phi^{*}_{\V}(G)`
  with their displays, the surrounding passage on Exercise 6.19, and the
  statement that they do not depend on the basepoint, physical p. 234
  (printed p. 217);
- the definition of the random subdivision `G_{\nu}`, the definition of an
  exponential tail with its moment equivalent, and Exercise 6.23, physical
  p. 238 (printed p. 221);
- the definitions of `E(K)` and `E^{*}(K)` that constitute the notation of
  (6.33) and the identities relating them to `\partial_{\E}K`, physical p. 217
  (printed p. 200);
- the definition of `\Phi^{**}_{\E}`, the two comparisons with
  `\Phi^{*}_{\E}` in general and the equality for trees, and Theorem 6.50,
  physical p. 238 (printed p. 221);
- the closing display of the proof of Theorem 6.50, the author's necessity
  remark citing this exercise, and the Galton–Watson argument that reuses this
  exercise's mechanism, physical p. 240 (printed p. 223).

All are printed as the author wrote them; none is paraphrased, corrected or
filled in.

## Literal source features kept as printed

1. The asked constant is printed with a **single** star on both pages that carry
   the target: physical p. 252 yields three occurrences of `\Phi` each followed
   by exactly one raised asterisk at 6.30 pt and none followed by two, and
   physical p. 638 yields one occurrence with a single asterisk at 6.30 pt and
   none with two. The statement and the closing display of the Comment therefore
   carry the same printed symbol.
2. The **double-star** constant is a different printed symbol, set as two
   separate raised asterisks at 7.35 pt, and it occurs only on physical pp. 238
   and 240: p. 238 has six double-star occurrences against seven single, p. 240
   has six double against eight single. It is transcribed as
   `\Phi^{**}_{\E}` exactly there.
3. The unanchored expansion constant of Exercise 6.23 on physical p. 238 carries
   no star at all; its `\Phi` is followed by the `\mathsf E` subscript directly.
4. The exponents of the Comment are true raised superscripts: the `n` of
   `2^{n}`, the `\epsilon` and `n` of `e^{-\epsilon n}`, the `2n` of
   `(1-e^{-\epsilon n})^{2n}`, and a further raised `2^{n}` measured at 5.25 pt,
   one level above the 6.30 pt script size of the exponents that carry it. The
   subscripts `i=1`, `1` of `L_{1}`, and `\E` of `\partial_{\E}` and
   `\Phi^{*}_{\E}` are baseline subscripts.
5. The Comment prints `L_{e}` and `\sum_{e\in E(S)}L_{e}` over the edge set
   `E(S)`, and `\partial_{\E}S` over the vertex set `S`; the denominator is
   neither `\sum_{e\in E^{*}(S)}L_{e}` nor `|E(S)|`, and it is not synchronized
   with the display of the Theorem 6.50 proof on physical p. 240, which uses
   `E^{*}(S)`. Both are transcribed as printed.
6. The law and its members are set in angle brackets, `\langle L_{i}\rangle` and
   `\langle L_{e}\rangle_{e\in\E(G)}`, and are transcribed as printed.
7. The space character after the symbol `\nu` is missing from the PDF text layer
   of every page of this exercise, not only from the Comment; the printed
   spacing is nevertheless ordinary, and no spacing difference between the
   Comment and the body is claimed.
8. The stretched delimiters of several formulas do not extract as delimiter
   characters: the text layer writes them as control bytes of the font
   `txex-bar`, whose byte value does not identify which delimiter is printed.
   The occurrences are enumerated on physical pp. 217, 233, 234, 240 and 252;
   physical pp. 238 and 638 carry no control byte at all. They are extraction
   artefacts of the delimiters and nothing is transcribed from them.
9. In the final display the numerator is printed as `2n+1` and the denominator
   as `cn`, and the following relation is the two-line approximation symbol
   `\approx`, not an equality.
10. The reflowed line breaks of the question and of the Comment are not content.

## Inspection basis

The rendered pages were not inspected as pixels. Five final pages were read as a
PDF text layer and the layout and source geometry were measured with
deterministic instruments:

- `runs/6_88/check_6_88_textlayer.py` — per-page characters and lines, 46
  anchor assertions, replacement/control characters, warning census, embedded
  fonts;
- `runs/6_88/check_6_88_layout.py` — page boxes, safe-box violations, line
  rectangles, line pitch, text top and bottom, with
  `runs/6_88/dump_and_overlap_6_88.py` re-measuring the intersecting pairs from
  explicit dumps of the seven source pages;
- `runs/6_88/measure_6_88_script_geometry.py` — per-span sizes, baselines and
  fonts, recorded in `script_geometry_6_88.json`, and
  `runs/6_88/census_stars_6_88.py` — a character walk after every capital `\Phi`
  on all seven source pages, recorded in `star_census_6_88.json`, which counts
  asterisk glyphs rather than spans and is the instrument the star statements
  above rest on;
- `runs/6_88/verify_claims_6_88.py` — word-by-word comparison of all 38 claimed
  passages with the source text layer.

## What this reader does not do

- It does not repair, strengthen or generalise anything. The separate errata
  sheet dated 19 August 2026 has exactly one Chapter 6 entry, the p. 616
  correction to Exercise 6.34; its only other entry touching Chapter 6 material,
  on p. 650, replaces two 2015 bibliographic items printed on pp. 509 and 510.
  No entry touches physical pp. 217, 233, 234, 238, 240, 252 or 638, so no
  revision is applied anywhere in this reader.
- It does not supply the Comment's missing first step: the passage from
  "`\nu` does not have an exponential tail" to the displayed inequalities is
  asserted by the author and is left asserted here.
- It does not certify the correctness of the source mathematics.
- It does not perform the finite semantic de-duplication; that is a separate
  artifact under `candidates/6_88/`.
- It does not assign a formal identifier, write a shared library, or support
  public redistribution.
