"""
INDEPENDENT second implementation of the reachable-state graph of serial
proposer-proposing deferred acceptance (DA), written from the mathematical
definition only.  Deliberately different from graph_audit_independent.py:

  * state is encoded RECEIVER-SIDE:  (holder, ptr)
        holder[r] = proposer currently held by receiver r, or -1
        ptr[p]    = number of proposals p has already made
    (the audited code encodes matching PROPOSER-side, m[p] = receiver of p)
  * exploration is BFS with an explicit deque (audited code: DFS via list.pop)
  * receiver preferences are consumed as explicit rank matrices built here
  * active/enabled set is recomputed from `holder` rather than from `m`

Supports incomplete lists (pref lists may be shorter than the receiver set)
and unbalanced instances.
"""
from collections import deque
from itertools import permutations, product


class Instance:
    """I = (P, R, E, >_P, >_R) with strict, possibly incomplete lists."""

    __slots__ = ("np", "nr", "P", "Rrank", "Rlist")

    def __init__(self, P, R):
        # P[p] : tuple of receivers, p's acceptable receivers in strict order
        # R[r] : tuple of proposers, r's acceptable proposers in strict order
        self.np = len(P)
        self.nr = len(R)
        self.P = tuple(tuple(x) for x in P)
        self.Rlist = tuple(tuple(x) for x in R)
        # rank[r][p] = position of p in r's list, or None if unacceptable
        self.Rrank = tuple({p: i for i, p in enumerate(row)} for row in self.Rlist)

    def accepts(self, r, challenger, incumbent):
        """Does receiver r prefer `challenger` to `incumbent` (-1 = nobody)?"""
        cr = self.Rrank[r].get(challenger)
        if cr is None:
            return False                      # r finds challenger unacceptable
        if incumbent == -1:
            return True
        ir = self.Rrank[r].get(incumbent)
        return cr < ir


def initial_state(I):
    return ((-1,) * I.nr, (0,) * I.np)


def active_proposers(I, s):
    """p is active iff p is currently unmatched and has an unproposed
    acceptable receiver left."""
    holder, ptr = s
    held = set(h for h in holder if h != -1)
    return tuple(p for p in range(I.np) if p not in held and ptr[p] < len(I.P[p]))


def local_update(I, s, p):
    """U_p(s).  Requires p active at s."""
    holder, ptr = s
    h = list(holder)
    q = list(ptr)
    r = I.P[p][q[p]]
    q[p] += 1
    if I.accepts(r, p, h[r]):
        h[r] = p              # incumbent (if any) becomes unmatched implicitly
    # else: p is rejected and stays unmatched
    return (tuple(h), tuple(q))


def reachable_graph(I):
    """Returns adjacency dict  state -> {proposer: successor state}."""
    s0 = initial_state(I)
    adj = {}
    queue = deque([s0])
    adj[s0] = None
    while queue:
        s = queue.popleft()
        outs = {}
        for p in active_proposers(I, s):
            t = local_update(I, s, p)
            outs[p] = t
            if t not in adj:
                adj[t] = None
                queue.append(t)
        adj[s] = outs
    return adj


# ---------------------------------------------------------------- utilities

def matching_from_state(s):
    """mu as a frozenset of (p, r) pairs, read off the receiver side."""
    holder, _ = s
    return frozenset((h, r) for r, h in enumerate(holder) if h != -1)


def all_complete_paths(I, adj, limit=None):
    """Every maximal sequence of proposer labels from s0 to a terminal state."""
    s0 = initial_state(I)
    out = []

    def rec(s, acc):
        if limit is not None and len(out) >= limit:
            return
        outs = adj[s]
        if not outs:
            out.append(tuple(acc))
            return
        for p, t in sorted(outs.items()):
            acc.append((p, s[1][p]))          # event = (proposer, proposal index)
            rec(t, acc)
            acc.pop()

    rec(s0, [])
    return out


def perm_profiles(n):
    """All complete strict profiles on n x n as (P, R) tuples of permutations."""
    perms = list(permutations(range(n)))
    for P in product(perms, repeat=n):
        for R in product(perms, repeat=n):
            yield P, R
