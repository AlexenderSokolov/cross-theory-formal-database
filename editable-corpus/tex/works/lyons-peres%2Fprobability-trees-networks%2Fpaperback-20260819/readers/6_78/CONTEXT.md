# Exercise 6.78 and its Author Comment — reader context

Source work: *Probability on Trees and Networks*, Russell Lyons and Yuval Peres.
Fixed source version: author paperback version 2026-08-19 (716 physical pages,
21,010,205 bytes), `original/book_pb.pdf`.

Page convention throughout this reader: `physical = printed + 17`.
The exercise statement is on physical p. 251 (printed p. 234); the author
Comment is on physical p. 637 (printed p. 620). The group the exercise names is
defined on physical p. 106 (printed p. 89); its exponential growth is shown on
physical pp. 106–107 (printed pp. 89–90); the expansion input behind the
matching upper bound is Theorem 6.29 on physical pp. 224–225 (printed
pp. 207–208), followed by Corollary 6.32 on physical pp. 225–226 (printed
pp. 208–209); the cited external work is in the bibliography on physical p. 696
(printed p. 679).

## What is in the reader

| span | lines | content |
| --- | --- | --- |
| context | 19–103 | source/scope statement, errata statement, six literal-feature items, the note that the exercise is not cited in the body, the definition of the lamplighter group, its exponential growth, Theorem 6.29 with the author's sharpness remark, and Corollary 6.32 (i), (ii), (iii) |
| `\clearpage` | 105 | page break so the primary statement starts a page |
| primary statement | 106–112 | Exercise 6.78 verbatim, including the sentence that the matching upper bound is Corollary 6.32(iii) |
| primary proof | 114–130 | the complete author Comment on Exercise 6.78 verbatim |
| cached attribution | 132–139 | the Pittet and Saloff-Coste (1999) entry as printed in the book's own bibliography, with the note that the work was not obtained or consulted here |

## Uncounted context carried in the reader

The Comment is not self-contained, so five passages are reprinted as context and
are not counted as part of the primary statement or the primary proof:

- the definition of the lamplighter group as a restricted wreath product, with
  its generators and the streetlamp reading, physical p. 106 (printed p. 89);
- the Fibonacci growth argument giving growth rate `(1+\sqrt5)/2`,
  physical pp. 106–107 (printed pp. 89–90);
- Theorem 6.29 (Expansion of Cayley Graphs) with its display
  `|\partial^{in}_{\V}K|/|K| \ge 1/(2R(2|K|))`, physical p. 224 (printed p. 207);
- the author's remark that both sides of Theorem 6.29 are of order `r` for
  boxes (6.8) in the lamplighter group, so the bound is sharp there up to
  constants, physical p. 225 (printed p. 208);
- Corollary 6.32 (i), (ii) and (iii) with their displays, including the
  `C_1\exp(-C_2n^{1/3})` of part (iii) and the sentence that part (iii) applies
  to a Cayley graph of exponential growth because of Theorem 6.29,
  physical pp. 225–226 (printed pp. 208–209).

All are printed as the author wrote them; none is paraphrased, corrected or
filled in.

## Literal source features kept as printed

1. The exercise prints the group as a blackboard-bold capital `Z` followed by a
   script-size circled dot set above the line, and the same two-glyph setting is
   used where the group is defined on physical p. 106. It is transcribed as
   `\Z^{\odot}`. The base letter is taken from the root session's own
   full-resolution viewing of physical p. 251 — not from this session's pixel
   reading, and not from the PDF text layer, where the letter is an unmapped
   byte of a math-italic font carrying no Unicode map and the circled dot comes
   out as the ordinary circled-dot character at script size.
2. Two control characters in the text layer of physical p. 251 sit at the two
   positions of the fence around the pair `(\Psi_j,X_j)`. They are extraction
   artefacts of that fence, not printed characters.
3. The exercise prints the lower bound for `p_{2n}(o,o)` and the Comment prints
   it for `p_n(o,o)`. On both pages the subscript characters are set at script
   size on the baseline, not raised, so both are ordinary subscripts and
   neither is an exponent. Neither is synchronized with the other and no index
   is changed.
4. The exponent `n^{1/3}` on physical p. 251 is raised above the line with the
   `1`, the solidus and the `3` all at script size, in contrast with the
   subscripts above; it is transcribed as printed.
5. The two `j`'s of the pair are set at script size; the printed line breaks
   inside the exercise are reflowed and are not content.
6. The constants `c`, `C` and `c_1` of the Comment, the ceiling
   `\lceil n/r^{2}\rceil` and the interval `[-2r,2r]` are transcribed as
   printed. No constant is identified with another and no small-`n` adjustment
   is inserted.

## Inspection basis

The rendered pages were not inspected as pixels. Four final pages were read as a
PDF text layer and the layout and source geometry were measured with
deterministic instruments:

- `runs/6_78/check_6_78_textlayer.py` — per-page characters and lines, 36
  anchor assertions, replacement/control characters, warning census, embedded
  fonts;
- `runs/6_78/check_6_78_layout.py` — page boxes, safe-box violations, line
  rectangles, line pitch, text top and bottom, with `runs/6_78/dump_and_overlap_6_78.py`
  re-measuring the intersecting pairs from explicit page dumps;
- `runs/6_78/measure_6_78_subscript_geometry.py` — per-span sizes, baselines and
  fonts for the two subscripts and the two `n^{1/3}` controls, plus the
  two-glyph group setting on physical pp. 251 and 106;
- `runs/6_78/verify_claims_6_78.py` — word-by-word comparison of all 34 claimed
  passages with the source text layer.

The group-symbol reading is the one item that no instrument in this list settles;
it is recorded above as the root session's source-page viewing.

## What this reader does not do

- It does not repair, strengthen or generalise anything. The separate errata
  sheet dated 19 August 2026 has exactly one Chapter 6 entry, the p. 616
  correction to Exercise 6.34; its one lamplighter-related entry, on p. 650,
  replaces two 2015 bibliographic items printed on pp. 509 and 510 and does not
  touch the 1999 item cited here or either page of this exercise. No revision is
  therefore applied anywhere in this reader.
- It does not certify the correctness of the source mathematics.
- It does not perform the finite semantic de-duplication; that is a separate
  artifact under `candidates/6_78/`.
- It does not assign a formal identifier, write a shared library, or support
  public redistribution.
