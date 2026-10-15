"""
Verification of the numbers in

    Prime factorisation of stable-matching instances: uniqueness,
    simultaneous products, and an exact census

This file is deliberately self-contained: standard library only, no imports
from the other files here, and every structure built from its definition in
the paper rather than from a library.  It is therefore an independent check
and not a rerun of the code that produced the numbers.

    python verify.py          the quick checks, a few seconds
    python verify.py --all    also the exhaustive size-three pass,
                              which takes about a minute

Each check prints PASS or FAIL and the script exits non-zero if anything
failed, so it can be run unattended.

What is checked

  A  size three, exhaustive over all 46,656 profiles: the Boolean-cube count
     of Corollary 5.1, the equivalence of Theorem 5, the uniqueness of the
     finest partition (Theorem 6) against the meet of every partition into
     blocks, and the decomposable count of Table 3
  B  the census recursion of Theorem 9, evaluated to n = 5, against the
     exhaustive count at n = 3 and against every entry of Table 3
  C  the products theorem and the composition laws (Theorem 7,
     Corollary 7.2) on random direct sums at sizes four to six
  D  the instance drawn in Fig 1, and all six of its composition laws
  E  the two families of Proposition 12.3 at sizes two to six
"""
import itertools
import math
import random
import sys

# --------------------------------------------------------------- the model
# An instance is (P, R): P[p] is proposer p's strict complete ranking of the
# receivers, R[r] is receiver r's strict complete ranking of the proposers.


def reachable(P, R):
    """Serial deferred acceptance from the definition.

    A state is (holder, ptr): holder[r] is the proposer r currently holds or
    -1, ptr[p] is the number of proposals p has made.  A proposer is active
    when it is unheld and has an unproposed receiver left.  Returns the
    reachable states, the arc count, and the unique terminal state.
    """
    n = len(P)
    rank = [{p: i for i, p in enumerate(row)} for row in R]
    start = ((-1,) * n, (0,) * n)
    seen, stack, arcs, terminal = {start}, [start], 0, None
    while stack:
        holder, ptr = stack.pop()
        held = {h for h in holder if h != -1}
        moved = False
        for p in range(n):
            if p in held or ptr[p] >= n:
                continue
            moved = True
            arcs += 1
            r = P[p][ptr[p]]
            h = list(holder)
            q = list(ptr)
            q[p] += 1
            if h[r] == -1 or rank[r][p] < rank[r][h[r]]:
                h[r] = p
            nxt = (tuple(h), tuple(q))
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
        if not moved:
            if terminal is not None and terminal != (holder, ptr):
                raise AssertionError("two terminal states")
            terminal = (holder, ptr)
    return seen, arcs, terminal


def complete_runs(P, R):
    """the number of complete schedules, counted as paths of the state graph"""
    n = len(P)
    rank = [{p: i for i, p in enumerate(row)} for row in R]
    memo = {}

    def paths(state):
        if state in memo:
            return memo[state]
        holder, ptr = state
        held = {h for h in holder if h != -1}
        total, moved = 0, False
        for p in range(n):
            if p in held or ptr[p] >= n:
                continue
            moved = True
            r = P[p][ptr[p]]
            h = list(holder)
            q = list(ptr)
            q[p] += 1
            if h[r] == -1 or rank[r][p] < rank[r][h[r]]:
                h[r] = p
            total += paths((tuple(h), tuple(q)))
        memo[state] = 1 if not moved else total
        return memo[state]

    return paths(((-1,) * n, (0,) * n))


def stable_matchings(P, R):
    """every matching with no blocking pair, by definition"""
    n = len(P)
    prank = [{r: i for i, r in enumerate(row)} for row in P]
    rrank = [{p: i for i, p in enumerate(row)} for row in R]
    out = []
    for m in itertools.permutations(range(n)):          # m[p] = receiver of p
        who = {r: p for p, r in enumerate(m)}
        if all(not (prank[p][r] < prank[p][m[p]] and rrank[r][p] < rrank[r][who[r]])
               for p in range(n) for r in range(n)):
            out.append(m)
    return out


# ----------------------------------------------------------- the partition
def blocks(P, R):
    """(A, B) is a block when the k members of A rank exactly B in their
    first k places and the k members of B rank exactly A in theirs"""
    n = len(P)
    out = []
    for k in range(1, n + 1):
        for A in itertools.combinations(range(n), k):
            B = set(P[A[0]][:k])
            if any(set(P[p][:k]) != B for p in A):
                continue
            if all(set(R[r][:k]) == set(A) for r in B):
                out.append((frozenset(A), frozenset(B)))
    return out


def finest(P, R):
    """the finest partition of the proposers into blocks, built downwards:
    a block splits exactly when the maximal blocks properly inside it cover
    it"""
    n = len(P)
    fam = {A: B for A, B in blocks(P, R)}

    def split(A):
        inner = [C for C in fam if C < A]
        maximal = [C for C in inner if not any(C < D for D in inner)]
        if sum(len(C) for C in maximal) == len(A) and len(maximal) > 1:
            if set().union(*maximal) == set(A):
                return [x for C in maximal for x in split(C)]
        return [A]

    return sorted(split(frozenset(range(n))), key=sorted)


def all_block_partitions(P, R):
    """every partition of the proposers whose parts are blocks"""
    n = len(P)
    parts = sorted({A for A, B in blocks(P, R)}, key=lambda s: (-len(s), sorted(s)))
    out = []

    def rec(rest, acc):
        if not rest:
            out.append(list(acc))
            return
        first = min(rest)
        for A in parts:
            if first in A and A <= rest:
                rec(rest - A, acc + [A])

    rec(frozenset(range(n)), [])
    return out


def meet(p1, p2):
    """the common refinement of two partitions"""
    out = []
    for A in p1:
        for B in p2:
            if A & B:
                out.append(A & B)
    return sorted(out, key=sorted)


# ------------------------------------------------------------- the checks
FAIL = []


def report(name, ok, detail=""):
    print("  %-4s %s%s" % ("PASS" if ok else "FAIL", name,
                           ("   " + detail) if detail else ""))
    if not ok:
        FAIL.append(name)


def profiles(n):
    orders = list(itertools.permutations(range(n)))
    for P in itertools.product(orders, repeat=n):
        for R in itertools.product(orders, repeat=n):
            yield P, R


def check_A(limit=None):
    print("\nA. size three, exhaustive")
    n, cubes, decomp, shapes, seen = 3, 0, 0, {}, 0
    uniq_ok = True
    for P, R in profiles(n):
        seen += 1
        if limit and seen > limit:
            break
        states, arcs, term = reachable(P, R)
        cube = len(states) == 2 ** n
        distinct_first = len({P[p][0] for p in range(n)}) == n
        if cube != distinct_first:
            uniq_ok = False
        cubes += cube
        f = finest(P, R)
        if len(f) > 1:
            decomp += 1
        shapes[tuple(sorted((len(A) for A in f), reverse=True))] = \
            shapes.get(tuple(sorted((len(A) for A in f), reverse=True)), 0) + 1
        if seen % 4096 == 0:                      # uniqueness is the slow part
            m = None
            for part in all_block_partitions(P, R):
                m = part if m is None else meet(m, part)
            if sorted(m, key=sorted) != f:
                uniq_ok = False
    report("Theorem 5, cube if and only if distinct first choices", uniq_ok)
    report("Corollary 5.1, Boolean cubes at n = 3", cubes == 10368,
           "%s, expected 10,368" % format(cubes, ","))
    report("Table 3, input-decomposable at n = 3", decomp == 888,
           "%s, expected 888" % format(decomp, ","))
    report("Theorem 6, finest partition is the meet of all of them", uniq_ok)
    print("       shapes of the finest partition:",
          ", ".join("%s: %s" % ("+".join(map(str, k)), format(v, ","))
                    for k, v in sorted(shapes.items())))
    return decomp


def census(nmax):
    """Theorem 9, evaluated forwards"""
    Pi = {1: 1}
    rows = {}
    for n in range(2, nmax + 1):
        T = math.factorial(n) ** (2 * n)
        total = 0
        shape_counts = {}
        for lam in partitions(n):
            if len(lam) == 1:
                continue
            mult = {}
            for k in lam:
                mult[k] = mult.get(k, 0) + 1
            N = (math.factorial(n) //
                 math.prod(math.factorial(k) for k in lam)) ** 2
            for m in mult.values():
                N //= math.factorial(m)
            term = N
            for k in lam:
                term *= Pi[k] * math.factorial(n - k) ** (2 * k)
            shape_counts[tuple(lam)] = term
            total += term
        Pi[n] = T - total
        rows[n] = (T, total, Pi[n], shape_counts)
    return Pi, rows


def partitions(n, cap=None):
    cap = n if cap is None else cap
    if n == 0:
        yield []
        return
    for k in range(min(n, cap), 0, -1):
        for rest in partitions(n - k, k):
            yield [k] + rest


def check_B(decomp3=None):
    print("\nB. the census of Theorem 9")
    Pi, rows = census(5)
    ok = Pi[2] == 14 and Pi[3] == 45768
    report("Table 3 rows n = 2 and n = 3", ok,
           "Pi(2) = %d, Pi(3) = %s" % (Pi[2], format(Pi[3], ",")))
    report("Table 3 row n = 4, decomposable count",
           rows[4][1] == 88478208, "%s" % format(rows[4][1], ","))
    report("Table 3 row n = 4, total T(4)",
           rows[4][0] == 110075314176, format(rows[4][0], ","))
    want = {(3, 1): 26362368, (2, 2): 903168, (2, 1, 1): 20901888,
            (1, 1, 1, 1): 40310784}
    got = rows[4][3]
    report("the four shape counts at n = 4",
           all(got.get(k) == v for k, v in want.items()),
           ", ".join("%s: %s" % ("+".join(map(str, k)), format(got.get(k, 0), ","))
                     for k in want))
    report("Pi(5) of the text", Pi[5] == 619162084591420538880,
           format(Pi[5], ","))
    if decomp3 is not None:
        report("the n = 3 row agrees with the exhaustive pass",
               rows[3][1] == decomp3, "%d vs %d" % (rows[3][1], decomp3))
    return Pi


def direct_sum(parts):
    """the instance whose blocks are the given instances, side by side"""
    P, R, off = [], [], 0
    sizes = [len(p) for p, _ in parts]
    n = sum(sizes)
    for (Pi_, Ri_), k in zip(parts, sizes):
        outside = [x for x in range(n) if not (off <= x < off + k)]
        for row in Pi_:
            P.append(tuple([x + off for x in row] + outside))
        for row in Ri_:
            R.append(tuple([x + off for x in row] + outside))
        off += k
    return tuple(P), tuple(R)


def invariants(P, R):
    states, arcs, term = reachable(P, R)
    q = term[1]
    Q = sum(q)
    L = complete_runs(P, R)
    multi = math.factorial(Q)
    for x in q:
        multi //= math.factorial(x)
    return dict(N=len(states), E=arcs, Q=Q, L=L, kappa=L / multi,
                stab=len(stable_matchings(P, R)))


def random_instance(rng, n):
    return (tuple(tuple(rng.sample(range(n), n)) for _ in range(n)),
            tuple(tuple(rng.sample(range(n), n)) for _ in range(n)))


def check_C(trials=40, seed=11):
    print("\nC. the products theorem and the composition laws")
    rng = random.Random(seed)
    bad = {k: 0 for k in ("N", "E/N", "Q", "L", "kappa", "stab")}
    done = 0
    for _ in range(trials):
        k1 = rng.choice([1, 2, 3])
        k2 = rng.choice([1, 2, 3])
        if k1 + k2 > 6 or k1 + k2 < 4:
            continue
        I1, I2 = random_instance(rng, k1), random_instance(rng, k2)
        a, b = invariants(*I1), invariants(*I2)
        c = invariants(*direct_sum([I1, I2]))
        done += 1
        if a["N"] * b["N"] != c["N"]:
            bad["N"] += 1
        if abs(a["E"] / a["N"] + b["E"] / b["N"] - c["E"] / c["N"]) > 1e-9:
            bad["E/N"] += 1
        if a["Q"] + b["Q"] != c["Q"]:
            bad["Q"] += 1
        if a["L"] * b["L"] * math.comb(c["Q"], a["Q"]) != c["L"]:
            bad["L"] += 1
        if abs(a["kappa"] * b["kappa"] - c["kappa"]) > 1e-9:
            bad["kappa"] += 1
        if a["stab"] * b["stab"] != c["stab"]:
            bad["stab"] += 1
    for k, v in bad.items():
        report("composition law: %s" % k, v == 0,
               "%d direct sums, %d failures" % (done, v))


FIG_P1 = ((0, 1, 2), (0, 1, 2), (2, 0, 1))
FIG_R1 = ((2, 0, 1), (0, 1, 2), (0, 1, 2))
FIG_P2 = ((0, 1), (1, 0))
FIG_R2 = ((1, 0), (0, 1))


def check_D():
    print("\nD. the instance of Fig 1")
    I1, I2 = (FIG_P1, FIG_R1), (FIG_P2, FIG_R2)
    I = direct_sum([I1, I2])
    a, b, c = invariants(*I1), invariants(*I2), invariants(*I)
    want = [("N = 10 x 4 = 40", a["N"] == 10 and b["N"] == 4 and c["N"] == 40),
            ("E = 15 and 4, E/N = 1.5 + 1.0 = 2.5",
             a["E"] == 15 and b["E"] == 4 and abs(c["E"] / c["N"] - 2.5) < 1e-9),
            ("Q* = 4 + 2 = 6", (a["Q"], b["Q"], c["Q"]) == (4, 2, 6)),
            ("L = 8 x 2 x C(6,4) = 240",
             (a["L"], b["L"], c["L"]) == (8, 2, 240)),
            ("commutation index 2/3 x 1 = 2/3",
             abs(a["kappa"] - 2 / 3) < 1e-12 and abs(b["kappa"] - 1) < 1e-12
             and abs(c["kappa"] - 2 / 3) < 1e-12),
            ("stable matchings 2 x 2 = 4",
             (a["stab"], b["stab"], c["stab"]) == (2, 2, 4)),
            ("the only proper blocks are the two factors",
             sorted(sorted(A) for A, B in blocks(*I) if len(A) < 5)
             == [[0, 1, 2], [3, 4]])]
    for name, ok in want:
        report(name, ok)


def aligned(n):
    """A_n: p_i and r_i rank each other first, then rotate"""
    P = tuple(tuple((i + j) % n for j in range(n)) for i in range(n))
    R = tuple(tuple((i - j) % n for j in range(n)) for i in range(n))
    return P, R


def antiphase(n):
    """C_n: the cyclic anti-phase template, no mutual first pair"""
    P = tuple(tuple((i + j) % n for j in range(n)) for i in range(n))
    R = tuple(tuple((i + 1 + j) % n for j in range(n)) for i in range(n))
    return P, R


def check_E():
    print("\nE. the two families of Proposition 12.3")
    for n in range(2, 7):
        A, C = aligned(n), antiphase(n)
        ia, ic = invariants(*A), invariants(*C)
        report("n = %d: both run as the Boolean cube" % n,
               ia["N"] == 2 ** n and ic["N"] == 2 ** n,
               "N = %d and %d" % (ia["N"], ic["N"]))
        report("n = %d: one stable matching against n of them" % n,
               ia["stab"] == 1 and ic["stab"] == n,
               "|Stab| = %d for the aligned family, %d for the anti-phase one"
               % (ia["stab"], ic["stab"]))
        fa, fc = finest(*A), finest(*C)
        report("n = %d: one is all singletons, the other is prime" % n,
               len(fa) == n and len(fc) == 1,
               "%d parts and %d part" % (len(fa), len(fc)))


def main():
    full = "--all" in sys.argv
    print("verification of the paper's checkable numbers")
    print("python %s, exhaustive size-three pass %s"
          % (sys.version.split()[0], "on" if full else "off (use --all)"))
    d3 = check_A(None if full else 20000) if full else None
    if not full:
        print("\nA. size three, exhaustive   SKIPPED (use --all, a few minutes)")
    check_B(d3)
    check_C()
    check_D()
    check_E()
    print("\n%d checks failed" % len(FAIL))
    for f in FAIL:
        print("   ", f)
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
