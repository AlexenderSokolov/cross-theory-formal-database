# Exercise 6.74 and its Author Comment — reader context

Source work: *Probability on Trees and Networks*, Russell Lyons and Yuval Peres.
Fixed source version: author paperback version 2026-08-19 (716 physical pages,
21,010,205 bytes), `original/book_pb.pdf`.

Page convention throughout this reader: `physical = printed + 17`.
The exercise statement is on physical p. 251 (printed p. 234); the author
Comment is on physical p. 637 (printed p. 620).

## What is in the reader

| span | lines | content |
| --- | --- | --- |
| context | 19–59 | source/scope statement, errata statement, four literal-feature items, the note that the exercise is used but not stated in the body, the definition of the edge boundary |
| `\clearpage` | 61 | page break so the primary statement starts a page |
| primary statement | 62–72 | Exercise 6.74 verbatim, including the sentence that the edge boundary is taken within the box and that this is therefore not a special case of Theorem 6.22 |
| primary proof | 74–89 | the complete author Comment on Exercise 6.74 verbatim, plus the cached-attribution note |

## Uncounted context carried in the reader

The Comment is not self-contained, so two passages are reprinted as context and
are not counted as part of the primary statement or the primary proof:

- the definition of the edge boundary: `|K|_D` and `|\partial_{\E}K|_c`,
  physical p. 194 (printed p. 177);
- the named input: Theorem 6.22 with its display
  `|\partial_{\E}A| \ge 2d\,|A|^{(d-1)/d}` and cube example, the remark that
  the bound for the box follows from Theorem 6.29, the projection maps
  `P_i(x_1,\dots,x_d) = (x_1,\dots,x_{i-1},x_{i+1},\dots,x_d)`, and
  Lemma 6.23, `|A|^{d-1} \le \prod_{i=1}^{d}|P_i(A)|`, all on physical p. 220
  (printed p. 203).

Both are printed as the author wrote them; neither is paraphrased, corrected or
filled in.

## Literal source features kept as printed

1. The hypothesis is printed `|A| < n^d/2` on both pages — the `d` is set at
   script size and raised above the line while the solidus and the `2` sit at
   body size on the baseline, in contrast to `n^{1/3}` on the same p. 251 where
   all three characters are set at script size. Neither page prints
   `n^{d/2}`.
2. The Comment writes the product bound as following from "Theorem 6.22"; the
   product inequality displayed there is Lemma 6.23's. Kept as printed.
3. The exercise says `A` is "a subgraph of the box", while the Comment writes
   `A \subset \{0,\dots,n-1\}^d`. Both are kept as printed.
4. The constant `C_d` is left unidentified: it is not equated with the
   Comment's explicit `(1-2^{-1/d})`, and no small-`n` adjustment is inserted.

## Inspection basis

The rendered pages were not inspected as pixels. Three final pages were read as
a PDF text layer and the layout was measured with geometric instruments:

- `runs/6_74/check_6_74_textlayer.py` — per-page characters and lines, anchors,
  replacement/control characters, warning census, embedded fonts;
- `runs/6_74/check_6_74_layout.py` — page boxes, safe-box violations, line
  rectangles, line pitch, text top and bottom;
- `runs/6_74/measure_6_74_hypothesis_geometry.py` — per-span sizes and
  baselines on physical pp. 251 and 637, with `n^{1/3}` as a control;
- `runs/6_74/verify_claims_6_74.py` — word-by-word comparison of all 16 claimed
  passages with the source text layer.

## What this reader does not do

- It does not repair, strengthen or generalise anything. The separate errata
  sheet dated 19 August 2026 has exactly one Chapter 6 entry, the p. 616
  correction to Exercise 6.34, which does not touch Exercise 6.74, so no
  revision is applied anywhere in this reader.
- It does not certify the correctness of the source mathematics.
- It does not perform the finite semantic de-duplication; that is a separate
  artifact under `candidates/6_74/`.
- It does not assign a formal identifier, write a shared library, or support
  public redistribution.
