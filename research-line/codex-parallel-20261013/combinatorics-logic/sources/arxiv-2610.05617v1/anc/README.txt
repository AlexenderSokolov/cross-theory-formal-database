Ancillary files for

    Prime factorisation of stable-matching instances: uniqueness,
    simultaneous products, and an exact census
    Yoshiteru Ishida

Everything here runs on a plain Python 3 installation. Only figure.py needs
anything outside the standard library, and what it needs is matplotlib.

The full repository is at https://github.com/i4dagh/smprime, archived at
doi:10.5281/zenodo.22984730.

    verify.py       the paper's checkable numbers, re-derived
    crosscheck.py   the two implementations of the algorithm, compared
    da_core.py      the second implementation
    figure.py       redraws Fig 1 from the definitions
    asymp.py        the asymptotics of Corollary 9.1, in exact arithmetic

verify.py
---------
    python verify.py          the quick checks, a few seconds
    python verify.py --all    also the exhaustive size-three pass, about a
                              minute

Each check prints PASS or FAIL and the script exits non-zero if any of them
failed. It is deliberately self-contained: standard library only, no imports
from the other files here, and every structure built from its definition in
the paper. It is therefore an independent check rather than a rerun of the
code that produced the numbers. It checks

  A  size three, exhaustively over all 46,656 profiles: the Boolean-cube
     count of Corollary 5.1, the equivalence of Theorem 5, the uniqueness of
     the finest partition of Theorem 6 against the meet of every partition
     into blocks, and the decomposable count of Table 3
  B  the census recursion of Theorem 9, evaluated to n = 5, against that
     exhaustive count and against every entry of Table 3, including the four
     shape counts at n = 4
  C  the products theorem and all six composition laws, on random direct
     sums at sizes four to six
  D  the instance drawn in Fig 1, and each of its six composition laws
  E  the two families of Proposition 12.3, at sizes two to six

crosscheck.py
-------------
    python crosscheck.py        size three exhaustively, then samples at
                                sizes four and five
    python crosscheck.py 4 500  500 random instances of size four

The paper says that every exhaustive count was produced twice, by two
implementations written independently of each other. This is that claim, made
runnable. The implementation inside verify.py explores states proposer-side
by depth-first search; da_core.py encodes a state receiver-side, explores
breadth-first with an explicit queue, keeps receiver preferences as rank
matrices, and recomputes the active set from the holder vector rather than
from the matching. They share no code. On all 46,656 size-three instances,
and on random instances at sizes four and five, they agree on the number of
reachable states, the number of arcs, and the terminal state.

da_core.py
----------
The second implementation, as used in the work behind the paper. It supports
incomplete preference lists and unbalanced instances as well, which the paper
does not need.

figure.py
---------
    python figure.py

Writes fig_products.pdf and fig_products.png next to itself. Every quantity
shown in the figure - the state counts, the arc counts, the proposal totals,
the complete-schedule counts, the commutation indices and the stable-set
sizes - is computed from the definitions when the figure is drawn, not copied
from the text. Requires matplotlib.

asymp.py
--------
    python asymp.py           to n = 12, under a minute
    python asymp.py 14        further, more slowly

Corollary 9.1 in exact integer and rational arithmetic: no sampling and no
floating point anywhere in the derivation. It evaluates the census recursion
of Theorem 9, checks that the identity closes at every size, and then checks
the three statements the corollary rests on - that the all-singletons term is
exactly the fraction n!/n^(2n) of T(n), that the shape (2, 1^(n-2)) is
exactly 7n/(2(n-1)^3) of it, and that the shape (2, 2, 1^(n-4)) is exactly
49n(n-2)(n-3)/(8(n-1)^7) - as assertions, so the script fails loudly if any
of them is wrong. It then prints the remaining share scaled by n^4 and n^6,
which is the numerical side of the O(n^(-4)) remainder.

Scope
-----
Strict and complete preference lists on both sides, equal numbers of
proposers and receivers, and a serial scheduler that activates one unmatched
proposer at a time. Nothing here should be read as applying to ties,
synchronous updates, many-to-one markets or matching with contracts.
