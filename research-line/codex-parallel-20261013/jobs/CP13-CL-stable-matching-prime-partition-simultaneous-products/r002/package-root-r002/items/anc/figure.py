"""
Fig 1: one partition, three products.

Section 4 states that a single partition of the agents, defined by a
condition on the ranked input alone, simultaneously induces a Cartesian
product of execution graphs, a direct sum of proposal-prefix antimatroids,
and a product of stable-matching lattices.  The figure shows one instance in
which all three are visible at once, and in which every composition law of
Corollary 7.2 can be read off as arithmetic.

The instance is I = I1 + I2 on five proposers and five receivers.  I1 is a
size-three instance with no proper block and two stable matchings; I2 is the
opposed size-two instance, also blockless, with two stable matchings.  The
only blocks of I are {p1,p2,p3}, {p4,p5} and the whole instance, so the
finest input-independent partition is the two-part one and nothing finer
exists.  Everything drawn here is computed from the definitions by the
independent implementation in da_core.py, not read from the manuscript.

  I1   N = 10   E = 15   E/N = 1.5   Q* = 4   L = 8     kappa = 2/3
  I2   N =  4   E =  4   E/N = 1.0   Q* = 2   L = 2     kappa = 1
  I    N = 40   E = 100  E/N = 2.5   Q* = 6   L = 240   kappa = 2/3

usage: python figure.py
"""
import os
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
# embed TrueType rather than Type 3, which arXiv prefers not to see
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyBboxPatch, Circle,
                                FancyArrowPatch, Rectangle)

HERE = os.path.dirname(os.path.abspath(__file__))
from verify import reachable, stable_matchings


def adjacency(P, R):
    """the reachable state graph as {pointer vector: {proposer: successor}}"""
    n = len(P)
    rank = [{p: i for i, p in enumerate(row)} for row in R]
    out = {}
    for holder, ptr in reachable(P, R)[0]:
        held = {h for h in holder if h != -1}
        outs = {}
        for p in range(n):
            if p in held or ptr[p] >= n:
                continue
            q = list(ptr)
            q[p] += 1
            outs[p] = tuple(q)
        out[ptr] = outs
    return out


INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8880"
SURFACE = "#fcfcfb"
BLUE, ORANGE = "#1d5aa8", "#c05a22"
BLUE_L, ORANGE_L = "#7fa1cb", "#e0a884"
BOX_F, BOX_E = "#eef3fb", "#9bb4d6"
BOX_F2, BOX_E2 = "#fdf1e8", "#e0b08c"

P1 = ((0, 1, 2), (0, 1, 2), (2, 0, 1))
R1 = ((2, 0, 1), (0, 1, 2), (0, 1, 2))
P2 = ((0, 1), (1, 0))
R2 = ((1, 0), (0, 1))
P = tuple([tuple(list(p) + [3, 4]) for p in P1]
          + [tuple([x + 3 for x in p] + [0, 1, 2]) for p in P2])
R = tuple([tuple(list(r) + [3, 4]) for r in R1]
          + [tuple([x + 3 for x in r] + [0, 1, 2]) for r in R2])


# ------------------------------------------------------------------ the graphs
def graph(Pp, Rr):
    """pointer-vector digraph: {v: {proposer: w}}, by Lemma 1 a faithful
    picture of the state graph"""
    return adjacency(Pp, Rr)


def layout(g):
    """x = proposals made so far; inside a level the nodes are ordered by
    barycentre sweeps, which is the standard way to take crossings out of a
    layered drawing"""
    lev = defaultdict(list)
    for v in g:
        lev[sum(v)].append(v)
    ks = sorted(lev)
    order = {k: sorted(lev[k]) for k in ks}
    up = defaultdict(list)
    for v, outs in g.items():
        for w in outs.values():
            up[w].append(v)

    def ypos():
        return {v: (0.0 if len(order[k]) == 1
                    else i - (len(order[k]) - 1) / 2.0)
                for k in ks for i, v in enumerate(order[k])}

    for sweep in range(8):
        y = ypos()
        for k in ks[1:] if sweep % 2 == 0 else ks[:-1][::-1]:
            nbr = (up if sweep % 2 == 0
                   else {v: list(g[v].values()) for v in order[k]})
            order[k].sort(key=lambda v: (sum(y[u] for u in nbr.get(v, []))
                                         / max(1, len(nbr.get(v, []))), v))
    y = ypos()
    return {v: (float(sum(v)), y[v]) for v in g}


def draw_graph(ax, g, pos, sx, sy, ox, oy, colour, rad, lw, ms, zbase=10):
    for v, outs in g.items():
        x0, y0 = ox + sx * pos[v][0], oy + sy * pos[v][1]
        for w in outs.values():
            x1, y1 = ox + sx * pos[w][0], oy + sy * pos[w][1]
            ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                         connectionstyle="arc3,rad=%.3f" % rad,
                                         arrowstyle="-", linewidth=lw,
                                         color=colour, alpha=0.85,
                                         zorder=zbase))
    for v in g:
        x0, y0 = ox + sx * pos[v][0], oy + sy * pos[v][1]
        ax.add_patch(Circle((x0, y0), ms, facecolor=colour, edgecolor="none",
                            zorder=zbase + 2))


# ------------------------------------------------------------------- panel (a)
def panel_instance(ax):
    n = 5
    Rrank = [{p: i for i, p in enumerate(row)} for row in R]
    for p in range(n):
        for r in range(n):
            i = P[p].index(r) + 1
            j = Rrank[r][p] + 1
            same = (p < 3) == (r < 3)
            ax.text(r, -p, "%d,%d" % (i, j), ha="center", va="center",
                    fontsize=6.6, color=INK if same else MUTED,
                    alpha=1.0 if same else 0.45)
    for lo, hi, f, e in ((0, 2, BOX_F, BOX_E), (3, 4, BOX_F2, BOX_E2)):
        ax.add_patch(FancyBboxPatch((lo - 0.45, -hi - 0.42),
                                    hi - lo + 0.9, hi - lo + 0.84,
                                    boxstyle="round,pad=0.02,rounding_size=0.10",
                                    facecolor=f, edgecolor=e, linewidth=1.0,
                                    zorder=0))
    for r in range(n):
        ax.text(r, 0.72, "r%d" % (r + 1), ha="center", va="center",
                fontsize=6.4, color=ORANGE)
    for p in range(n):
        ax.text(-1.05, -p, "p%d" % (p + 1), ha="center", va="center",
                fontsize=6.4, color=BLUE)
    ax.text(1.0, -5.05, "I₁", ha="center", va="center", fontsize=8.0,
            color=BLUE, fontweight="bold")
    ax.text(3.5, -5.05, "I₂", ha="center", va="center", fontsize=8.0,
            color=ORANGE, fontweight="bold")
    ax.set_xlim(-1.9, 4.9)
    ax.set_ylim(-5.7, 1.9)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.text(-1.9, 1.65, "(a)  the partition, from the input alone",
            ha="left", va="center", fontsize=7.4, color=INK,
            fontweight="bold")


# ------------------------------------------------------------------- panel (b)
def panel_factors(ax, g1, g2, pos1, pos2):
    draw_graph(ax, g1, pos1, 1.00, 0.62, 0.0, 0.0, BLUE, 0.09, 0.8, 0.055)
    ax.text(2.0, -1.45, "G(I₁)   N = 10, E = 15, Q* = 4",
            ha="center", va="center", fontsize=6.4, color=BLUE)
    draw_graph(ax, g2, pos2, 1.00, 0.62, 6.0, 0.0, ORANGE, 0.09, 0.8, 0.055)
    ax.text(7.0, -1.45, "G(I₂)   N = 4, E = 4, Q* = 2",
            ha="center", va="center", fontsize=6.4, color=ORANGE)
    ax.add_patch(Rectangle((4.95, -0.20), 0.40, 0.40, facecolor="none",
                           edgecolor=INK2, linewidth=1.0, zorder=5))
    ax.set_xlim(-0.6, 8.3)
    ax.set_ylim(-2.05, 2.05)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.text(-0.6, 1.85, "(b)  the two factor executions", ha="left",
            va="center", fontsize=7.4, color=INK, fontweight="bold")


# ------------------------------------------------------------------- panel (c)
def panel_stable(ax, st1, st2, st):
    def cell(x, y, m, colour, big):
        s = "".join(str(v + 1) for v in m)
        ax.text(x, y, s, ha="center", va="center", fontsize=7.4 if big else 6.8,
                color=colour, family="monospace")
    for j, b in enumerate(st2):
        cell(1.15 + 1.5 * j, 2.15, b, ORANGE, False)
    for i, a in enumerate(st1):
        cell(-0.55, 1.15 - 1.0 * i, a, BLUE, False)
    for i, a in enumerate(st1):
        for j, b in enumerate(st2):
            x, y = 1.15 + 1.5 * j, 1.15 - 1.0 * i
            ax.add_patch(FancyBboxPatch((x - 0.62, y - 0.30), 1.24, 0.60,
                                        boxstyle="round,pad=0.01,rounding_size=0.09",
                                        facecolor="#f4f6fa", edgecolor="#c9d3e2",
                                        linewidth=0.7, zorder=0))
            cell(x, y, tuple(list(a) + [v + 3 for v in b]), INK, True)
    for i in range(2):
        ax.add_patch(FancyArrowPatch((1.15 - 0.62 - 0.12, 1.15 - 1.0 * i),
                                     (-0.55 + 0.42, 1.15 - 1.0 * i),
                                     arrowstyle="-", linewidth=0.7,
                                     color="#c9d3e2", zorder=0))
    ax.text(1.15, -0.40, "Stab(I) = Stab(I₁) x Stab(I₂),   4 = 2 x 2",
            ha="center", va="center", fontsize=6.4, color=INK2)
    ax.set_xlim(-1.7, 4.0)
    ax.set_ylim(-0.95, 3.35)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.text(-1.7, 3.15, "(c)  and their stable sets", ha="left", va="center",
            fontsize=7.4, color=INK, fontweight="bold")


# ------------------------------------------------------------------- panel (d)
def panel_product(ax, g1, g2, pos1, pos2):
    """the blow-up drawing: one copy of G(I2) at every state of G(I1)"""
    SX, SY = 2.35, 1.30
    dx, dy = 0.30, 0.20

    def place(v, w):
        x = SX * pos1[v][0] + dx * (pos2[w][0] - 1.0)
        y = SY * pos1[v][1] + dy * pos2[w][1]
        return x, y

    for v in g1:                                   # factor-two arcs, inside
        for w, outs in g2.items():
            for u in outs.values():
                ax.add_patch(FancyArrowPatch(place(v, w), place(v, u),
                                             arrowstyle="-", linewidth=0.75,
                                             color=ORANGE, alpha=0.95,
                                             zorder=6))
    for v, outs in g1.items():                     # factor-one arcs, between
        for u in outs.values():
            for w in g2:
                ax.add_patch(FancyArrowPatch(place(v, w), place(u, w),
                                             arrowstyle="-", linewidth=0.55,
                                             color=BLUE, alpha=0.55,
                                             zorder=4))
    for v in g1:
        for w in g2:
            x, y = place(v, w)
            ax.add_patch(Circle((x, y), 0.062, facecolor=INK,
                                edgecolor="none", zorder=12))
    xs = [place(v, w)[0] for v in g1 for w in g2]
    ys = [place(v, w)[1] for v in g1 for w in g2]
    x0, ytop = min(xs) - 0.30, max(ys) + 0.62
    ax.text(x0, ytop,
            "G(I) is the Cartesian product of G(I₁) and G(I₂):   "
            "40 states, 100 arcs, six proposals to termination",
            ha="left", va="center", fontsize=7.0, color=INK)
    ax.text(min(xs) - 0.30, max(ys) + 0.28,
            "blue: a proposer of the first block moves     "
            "orange: a proposer of the second block moves",
            ha="left", va="center", fontsize=6.3, color=INK2)
    ax.set_xlim(min(xs) - 0.45, max(xs) + 0.45)
    ax.set_ylim(min(ys) - 0.40, max(ys) + 0.95)
    ax.set_aspect("equal")
    ax.set_axis_off()


# ------------------------------------------------------------------- panel (e)
ROWS = [("state count N", "10", "4", "40", "multiplicative"),
        ("arcs per state E/N", "1.5", "1.0", "2.5", "additive"),
        ("proposal total Q*", "4", "2", "6", "additive"),
        ("complete schedules L", "8", "2", "240", "8 x 2 x C(6,4)"),
        ("commutation index", "2/3", "1", "2/3", "multiplicative"),
        ("stable matchings", "2", "2", "4", "multiplicative")]


def panel_table(ax):
    xs = [0.015, 0.325, 0.435, 0.545, 0.685]
    head = ["invariant", "I₁", "I₂", "I", "law"]
    for x, h in zip(xs, head):
        ax.text(x, 0.93, h, ha="left", va="center", fontsize=6.6,
                color=INK, fontweight="bold")
    ax.plot([0.01, 0.99], [0.855, 0.855], color="#d6d4cd", linewidth=0.7)
    for i, row in enumerate(ROWS):
        y = 0.775 - 0.132 * i
        for x, cell, col in zip(xs, row, (INK, BLUE, ORANGE, INK, INK2)):
            ax.text(x, y, cell, ha="left", va="center", fontsize=6.5,
                    color=col)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    ax.set_title("(e)  every composition law of Corollary 7.2, on this one "
                 "instance", fontsize=7.6, color=INK, fontweight="bold",
                 pad=3, loc="left")


def main():
    g1, g2, g = graph(P1, R1), graph(P2, R2), graph(P, R)
    assert len(g1) == 10 and len(g2) == 4 and len(g) == 40
    assert sum(len(o) for o in g.values()) == 100
    st1, st2 = stable_matchings(P1, R1), stable_matchings(P2, R2)
    st = stable_matchings(P, R)
    assert len(st1) == 2 and len(st2) == 2 and len(st) == 4
    pos1, pos2 = layout(g1), layout(g2)

    fig = plt.figure(figsize=(7.1, 7.5))
    fig.patch.set_facecolor(SURFACE)
    outer = fig.add_gridspec(3, 1, height_ratios=[0.86, 1.30, 0.50],
                             hspace=0.10, left=0.015, right=0.985,
                             top=0.880, bottom=0.018)
    top = outer[0].subgridspec(1, 3, width_ratios=[0.95, 1.22, 0.95],
                               wspace=0.06)
    for ax, fn in ((fig.add_subplot(top[0, 0]), lambda a: panel_instance(a)),
                   (fig.add_subplot(top[0, 1]),
                    lambda a: panel_factors(a, g1, g2, pos1, pos2)),
                   (fig.add_subplot(top[0, 2]),
                    lambda a: panel_stable(a, st1, st2, st))):
        ax.set_facecolor(SURFACE)
        fn(ax)
    axp = fig.add_subplot(outer[1])
    axp.set_facecolor(SURFACE)
    axp.set_title("(d)  the execution of the whole instance is the Cartesian "
                  "product of the two factor executions",
                  fontsize=7.6, color=INK, fontweight="bold", pad=2)
    panel_product(axp, g1, g2, pos1, pos2)
    axt = fig.add_subplot(outer[2])
    axt.set_facecolor(SURFACE)
    panel_table(axt)

    fig.text(0.5, 0.985, "One partition, three products", ha="center",
             va="top", color=INK, fontsize=12.4, fontweight="bold")
    fig.text(0.5, 0.958,
             "A five-agent instance whose only proper blocks are {p1,p2,p3} "
             "and {p4,p5}. The partition is read off the ranked input "
             "alone,\nwith no reference to any run, and it nevertheless "
             "factors the execution, the antimatroid of proposal prefixes "
             "and the stable set\nat once. In (a) each cell is the pair (the "
             "proposer's rank of the receiver, the receiver's rank of the "
             "proposer).",
             ha="center", va="top", color=INK2, fontsize=6.5,
             linespacing=1.55)

    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(HERE, "fig_products.%s" % ext), dpi=240,
                    facecolor=SURFACE)
    print("wrote fig_products.pdf and .png")
    print("   N  %d x %d = %d" % (len(g1), len(g2), len(g)))
    print("   E  %d, E/N %.2f" % (sum(len(o) for o in g.values()),
                                  sum(len(o) for o in g.values()) / len(g)))
    print("   stable  %d x %d = %d" % (len(st1), len(st2), len(st)))


if __name__ == "__main__":
    main()
