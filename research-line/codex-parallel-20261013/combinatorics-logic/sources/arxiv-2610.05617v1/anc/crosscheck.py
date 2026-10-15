"""
The two implementations, compared.

verify.py builds the reachable state graph proposer-side, by depth-first
search over states (holder, ptr) from the definition of the algorithm.
da_core.py was written separately, encodes a state receiver-side, explores
breadth-first with an explicit queue, keeps receiver preferences as rank
matrices, and recomputes the active set from the holder vector rather than
from the matching.  The two share no code.

This script checks that they agree: the same number of reachable states, the
same arc count, and the same terminal state.  It runs exhaustively over all
46,656 size-three instances and on random instances at sizes four and five.

    python crosscheck.py           size three exhaustively, then samples
    python crosscheck.py 4 500     500 random instances of size four
"""
import random
import sys
from itertools import permutations, product

import da_core as dc
from verify import reachable


def one(P, R):
    """(states, arcs, terminal pointer vector) from each implementation"""
    states, arcs, term = reachable(P, R)
    adj = dc.reachable_graph(dc.Instance(P, R))
    other_arcs = sum(len(o or {}) for o in adj.values())
    other_term = [s for s, o in adj.items() if not o]
    return ((len(states), arcs, term[1]),
            (len(adj), other_arcs, other_term[0][1] if len(other_term) == 1
             else None))


def sweep(n, trials=None, seed=0):
    bad = 0
    if trials is None:
        orders = list(permutations(range(n)))
        cases = ((P, R) for P in product(orders, repeat=n)
                 for R in product(orders, repeat=n))
        total = len(orders) ** (2 * n)
    else:
        rng = random.Random(seed)
        cases = ((tuple(tuple(rng.sample(range(n), n)) for _ in range(n)),
                  tuple(tuple(rng.sample(range(n), n)) for _ in range(n)))
                 for _ in range(trials))
        total = trials
    done = 0
    for P, R in cases:
        a, b = one(P, R)
        done += 1
        if a != b:
            bad += 1
            if bad <= 3:
                print("   disagreement on P=%s R=%s: %s vs %s" % (P, R, a, b))
    print("  size %d: %s instances, %d disagreements  %s"
          % (n, format(done, ","), bad, "PASS" if bad == 0 else "FAIL"))
    return bad


if __name__ == "__main__":
    if len(sys.argv) == 3:
        sys.exit(1 if sweep(int(sys.argv[1]), int(sys.argv[2])) else 0)
    print("comparing the two implementations")
    bad = sweep(3)
    bad += sweep(4, 2000, 1)
    bad += sweep(5, 300, 2)
    sys.exit(1 if bad else 0)
