"""
Exact analysis of the decomposable fraction D(n)/T(n).

Theorem 9 gives

    T(n) = sum_{lambda |- n} N_lambda(n) prod_i Pi(k_i) ((n-k_i)!)^{2 k_i},
    N_lambda(n) = (1/prod_j m_j!) (n!/prod_i k_i!)^2,

and the s = 1 term is Pi(n).  Everything below is exact integer or exact
rational arithmetic: no sampling, no floating point in the derivation.

What is being checked:

  1  the all-singletons term is exactly n! / n^{2n} of T(n);
  2  the lambda = (2, 1^{n-2}) term is exactly  7n / (2 (n-1)^3)  of the
     all-singletons term;
  3  everything else is O(n^{-4}) relative to the all-singletons term,
     so D(n)/T(n) = (n!/n^{2n}) (1 + 7n/(2(n-1)^3) + O(n^{-4})).

usage: python asymp.py [NMAX]
"""
import sys
from fractions import Fraction
from functools import lru_cache
from math import factorial


def partitions(n, cap=None):
    """Partitions of n as non-increasing tuples."""
    if cap is None:
        cap = n
    if n == 0:
        yield ()
        return
    for k in range(min(n, cap), 0, -1):
        for rest in partitions(n - k, k):
            yield (k,) + rest


def n_lambda(n, lam):
    """Number of paired block structures of shape lam."""
    mult = {}
    for k in lam:
        mult[k] = mult.get(k, 0) + 1
    denom = 1
    for m in mult.values():
        denom *= factorial(m)
    num = factorial(n)
    for k in lam:
        num //= factorial(k)
    q, r = divmod(num * num, denom)
    assert r == 0, "N_lambda is not an integer"
    return q


def term(n, lam):
    """The lambda-term of the census identity, exactly."""
    t = n_lambda(n, lam)
    for k in lam:
        t *= Pi(k) * factorial(n - k) ** (2 * k)
    return t


@lru_cache(maxsize=None)
def Pi(n):
    """Input-prime instances of size n, by the recursion of Theorem 9."""
    if n == 1:
        return 1
    total = factorial(n) ** (2 * n)
    for lam in partitions(n):
        if len(lam) > 1:
            total -= term(n, lam)
    return total


def main():
    nmax = int(sys.argv[1]) if len(sys.argv) > 2 - 1 else 12
    print("n   Pi(n) matches census   D/T vs n!/n^2n   (2,1^{n-2}) share   rest")
    print("-" * 78)
    for n in range(2, nmax + 1):
        T = factorial(n) ** (2 * n)
        singles = term(n, tuple([1] * n))
        D = sum(term(n, lam) for lam in partitions(n) if len(lam) > 1)
        assert D + Pi(n) == T, "census identity fails at n = %d" % n

        # 1  all-singletons share of T
        assert Fraction(singles, T) == Fraction(factorial(n), n ** (2 * n))

        # 2  the (2, 1^{n-2}) term against the closed form
        if n >= 3:
            lam2 = tuple([2] + [1] * (n - 2))
            r2 = Fraction(term(n, lam2), singles)
            closed = Fraction(7 * n, 2 * (n - 1) ** 3)
            assert r2 == closed, "closed form fails at n = %d: %s vs %s" % (
                n, r2, closed)
        else:
            r2 = Fraction(0)

        # 3  the rest
        rest = D - singles - (term(n, lam2) if n >= 3 else 0)
        r_rest = Fraction(rest, singles)
        excess = Fraction(D, T) / Fraction(factorial(n), n ** (2 * n)) - 1
        print("%2d   ok                   1 + %-14.6f %-18.6f %.3e"
              % (n, float(excess), float(r2), float(r_rest)))

    print()
    print("scaled residual  n^4 * (rest / all-singletons):")
    for n in range(4, nmax + 1):
        singles = term(n, tuple([1] * n))
        lam2 = tuple([2] + [1] * (n - 2))
        rest = (sum(term(n, lam) for lam in partitions(n) if len(lam) > 1)
                - singles - term(n, lam2))
        print("  n = %2d   %.4f" % (n, float(Fraction(rest, singles)) * n ** 4))


if __name__ == "__main__":
    main()
