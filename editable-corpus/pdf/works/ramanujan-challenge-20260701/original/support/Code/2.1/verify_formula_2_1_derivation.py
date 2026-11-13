"""Build exact certificates for the CMF proof of the challenge pi formula.

The proof strategy is mirrored in five executable stages:

* restrict the Gauss ``2F1`` conservative matrix field (CMF) to the
  ``(1, 1, 3)`` trajectory;
* use a rational coboundary matrix to replace the derivative coordinate by
  two consecutive hypergeometric values;
* rescale the resulting recurrence to the printed polynomial continued
  fraction (PCF);
* certify the algebra surrounding the Euler-integral saddle and the two
  limiting characteristic roots; and
* evaluate the two anchor values used by Pincherle's theorem and simplify
  the resulting tail.

The CMF and recurrence stages use ``ramanujantools`` discovery APIs:
``pFq`` generates the field, ``CMF.trajectory_matrix`` restricts it to the
chosen line, ``Matrix.companion_coboundary_matrix`` finds the consecutive-value
basis, and ``PCF.deflate_all`` produces the compact challenge coefficients.
The explicit matrices retained below are independent paper targets, not inputs
to those construction calls.

The script proves polynomial and rational identities exactly.  It also checks
the special anchor integrals exactly.  It does not formalize the cited
contiguous-relation theorem, Euler's integral formula, Stirling's formula,
Poincare--Perron, or Pincherle; instead it verifies their hypotheses and the
specialized algebra used when they are applied in the mathematical proof.
No comments below depend on equation or theorem numbers in the LaTeX source.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from functools import lru_cache

import mpmath as mp
import sympy as sp
from ramanujantools import Matrix, Position
from ramanujantools.cmf import pFq
from ramanujantools.pcf import PCF
from sympy.abc import n


# ``n`` is the recurrence and continued-fraction index used throughout the derivation.
# It is imported from ``sympy.abc`` to match the index object used by ramanujantools.
# ``x``, ``y``, and ``z`` are the three parameter axes of the Gauss 2F1 CMF.
# The paper uses ``z`` for the denominator parameter, so the executable
# notation follows it even though some software libraries call this axis ``c``.
x, y, z = sp.symbols("x y z")
# The Gauss hypergeometric argument is the specialization defining the pi-CMF.
HYPERGEOMETRIC_ARGUMENT = sp.Rational(1, 2)
# The unshifted hypergeometric base point is the point used in Appendix G.3.
BASE_POINT = (sp.Rational(1, 2),) * 3
# The trajectory direction is the one producing challenge formula (2.1).
TRAJECTORY = (1, 1, 3)
# ``pFq`` names the two numerator axes x0,x1 and the denominator axis y0.
# These private construction coordinates are mapped to the paper's x,y,z notation
# whenever a matrix with visible parameter names is returned.
LIBRARY_X0, LIBRARY_X1 = pFq.x_axes(2)
LIBRARY_Y0 = pFq.y_axes(1)[0]
# ``LIBRARY_TO_PAPER_AXES`` translates only notation; it changes no mathematics.
LIBRARY_TO_PAPER_AXES = {LIBRARY_X0: x, LIBRARY_X1: y, LIBRARY_Y0: z}


@dataclass(frozen=True)
class NumericalVerification:
    """Store the measured high-precision convergence result."""

    depth: int
    digits: int
    absolute_error: mp.mpf
    elapsed_seconds: float
    value: mp.mpf
    target: mp.mpf


@lru_cache
def hypergeometric_cmf() -> pFq:
    """Construct the specialized Gauss CMF through ``ramanujantools.cmf.pFq``."""

    # The library derives every basis matrix from the hypergeometric differential equation.
    return pFq(2, 1, HYPERGEOMETRIC_ARGUMENT)


def library_trajectory() -> Position:
    """Return the library-coordinate trajectory ``{x0:1, x1:1, y0:3}``."""

    # ``trajectory`` is a Position because CMF methods validate axes and path signs.
    trajectory = Position(
        {LIBRARY_X0: TRAJECTORY[0], LIBRARY_X1: TRAJECTORY[1], LIBRARY_Y0: TRAJECTORY[2]}
    )
    return trajectory


def library_start_position() -> Position:
    """Return the library-coordinate start ``{x0:1/2, x1:1/2, y0:1/2}``."""

    # ``start`` is kept separate so the proof's initial point is visible and testable.
    start = Position(
        {
            LIBRARY_X0: BASE_POINT[0],
            LIBRARY_X1: BASE_POINT[1],
            LIBRARY_Y0: BASE_POINT[2],
        }
    )
    return start


def cmf_basis_matrices() -> dict[sp.Symbol, Matrix]:
    """Return the library-generated CMF basis matrices in paper notation.

    ``pFq(2,1,1/2).M(axis)`` automatically derives the contiguous matrices.
    The only custom operation here is renaming library axes ``x0,x1,y0`` to
    the paper axes ``x,y,z``.
    """

    # ``cmf`` is the library's exact rank-two Gauss-hypergeometric CMF.
    cmf = hypergeometric_cmf()
    # ``matrix_x`` advances the first numerator parameter.
    matrix_x = Matrix(cmf.M(LIBRARY_X0).subs(LIBRARY_TO_PAPER_AXES))
    # ``matrix_y`` advances the second numerator parameter.
    matrix_y = Matrix(cmf.M(LIBRARY_X1).subs(LIBRARY_TO_PAPER_AXES))
    # ``matrix_z`` advances the denominator parameter.
    matrix_z = Matrix(cmf.M(LIBRARY_Y0).subs(LIBRARY_TO_PAPER_AXES))
    return {x: matrix_x, y: matrix_y, z: matrix_z}


def cmf_conservation_validation() -> bool:
    """Run ``CMF.validate_conserving`` on all three library-generated axes.

    The built-in method checks every pairwise square identity and raises if any
    face fails to commute.  Reaching the return statement therefore certifies
    all three CMF conservation relations.
    """

    # The library performs the pairwise exact matrix checks internally.
    hypergeometric_cmf().validate_conserving()
    return True


def trajectory_position(index: sp.Expr = n) -> dict[sp.Symbol, sp.Expr]:
    """Return the library-generated trajectory substitution in paper notation."""

    # ``substitution`` is computed by CMF.trajectory_substitution as start+n*trajectory.
    substitution = hypergeometric_cmf().trajectory_substitution(
        library_trajectory(), library_start_position(), n
    )
    # ``paper_position`` exposes the result using x,y,z rather than x0,x1,y0.
    paper_position = {
        x: substitution[LIBRARY_X0],
        y: substitution[LIBRARY_X1],
        z: substitution[LIBRARY_Y0],
    }
    return {
        axis: coordinate.subs({n: index})
        for axis, coordinate in paper_position.items()
    }


@lru_cache
def trajectory_matrix_113() -> Matrix:
    """Use ``CMF.trajectory_matrix`` to construct the full ``(1,1,3)`` step."""

    # The library chooses and multiplies the elementary path, then factors the result.
    return hypergeometric_cmf().trajectory_matrix(
        library_trajectory(), library_start_position(), n
    )


def expected_trajectory_matrix_113() -> Matrix:
    """Return the simplified closed form expected from the CMF walk."""

    # ``shared_product`` shortens the repeated factors in all four matrix entries.
    shared_product = (6 * n + 1) * (6 * n + 5)
    return Matrix(
        [
            [
                -3 * (n + 1) * shared_product / (8 * n**2 * (2 * n + 1)),
                3
                * shared_product
                * (10 * n**2 + 15 * n + 6)
                / (16 * n**2 * (2 * n + 1)),
            ],
            [
                3
                * (5 * n + 1)
                * shared_product
                / (4 * n**2 * (2 * n + 1) ** 2),
                -9
                * shared_product
                * (14 * n**2 + 13 * n + 2)
                / (8 * n**2 * (2 * n + 1) ** 2),
            ],
        ]
    )


@lru_cache
def companion_coboundary_matrix_113() -> Matrix:
    """Discover ``U(n)`` using ``Matrix.companion_coboundary_matrix``.

    For a rank-two trajectory matrix, the library constructs its Krylov basis:
    the first column is ``(1,0)^T`` and the second is the first column of
    ``T(n)``.  Consequently
    ``[F_n, G_n] U(n) = [F_n, F_(n+1)]``, which is the mathematical reason
    the automatically found coboundary exposes a scalar recurrence satisfying
    ``T(n) U(n+1) = U(n) C(n)``.
    """

    # This call replaces the paper transcription of all four entries of U(n).
    return trajectory_matrix_113().companion_coboundary_matrix(n)


def coboundary_basis_residual() -> Matrix:
    """Check ``U(n)[:, 1] = T(n)[:, 0]`` coefficient by coefficient."""

    # ``trajectory_column`` gives the coefficients expressing F_(n+1).
    trajectory_column = trajectory_matrix_113()[:, 0]
    # ``coboundary_column`` is the proposed second consecutive-value basis vector.
    coboundary_column = companion_coboundary_matrix_113()[:, 1]
    return (coboundary_column - trajectory_column).applyfunc(sp.cancel)


@lru_cache
def companion_matrix_113() -> Matrix:
    """Use ``Matrix.as_companion`` to companionize the trajectory automatically."""

    # The library both finds U(n) and evaluates U(n)^(-1) T(n) U(n+1).
    return trajectory_matrix_113().as_companion(n)


def expected_companion_matrix_113() -> Matrix:
    """Return the factored companion matrix used in the convergence proof."""

    # ``polynomial_a`` is the cubic that survives as the final PCF denominator term.
    polynomial_a = 220 * n**3 + 484 * n**2 + 301 * n + 42
    # ``common_denominator`` clears the rational factors in both companion coefficients.
    common_denominator = 16 * (n + 1) ** 2 * (2 * n + 3) ** 2 * (5 * n + 1)
    # ``top_right`` is the coefficient multiplying F_n in the recurrence for F_{n+2}.
    top_right = (
        9
        * (5 * n + 6)
        * (6 * n + 1)
        * (6 * n + 5)
        * (6 * n + 7)
        * (6 * n + 11)
        / common_denominator
    )
    # ``bottom_right`` is the coefficient multiplying F_{n+1}.
    bottom_right = (
        -6
        * (6 * n + 7)
        * (6 * n + 11)
        * polynomial_a
        / common_denominator
    )
    return Matrix([[0, top_right], [1, bottom_right]])


def companion_recurrence_coefficients() -> tuple[sp.Expr, sp.Expr]:
    """Return ``A(n), B(n)`` from ``F_(n+2) = A(n) F_(n+1) + B(n) F_n``."""

    # In row-vector companion form C=[[0,B],[1,A]], so the final column is (B,A).
    companion_matrix = companion_matrix_113()
    coefficient_a = companion_matrix[1, 1]
    coefficient_b = companion_matrix[0, 1]
    return coefficient_a, coefficient_b


@lru_cache
def raw_trajectory_pcf() -> PCF:
    """Convert the CMF trajectory to a polynomial PCF with ``PCF(Matrix)``.

    The constructor companionizes the trajectory matrix and normalizes the
    rational recurrence to polynomial coefficients.  This is the built-in
    discovery route for the raw PCF, rather than a transcription of its terms.
    """

    # ``PCF`` accepts the non-companion trajectory matrix and performs the conversion.
    return PCF(trajectory_matrix_113())


@lru_cache
def challenge_pcf() -> PCF:
    """Return the compact challenge PCF via ``PCF.deflate_all``."""

    # Complete library deflation removes every admissible common recurrence factor.
    return raw_trajectory_pcf().deflate_all()


def pcf_coefficients() -> tuple[sp.Expr, sp.Expr]:
    """Return the library-derived compact coefficients ``a_n,b_n``."""

    # The two properties expose the recurrence represented by the deflated PCF.
    continued_fraction = challenge_pcf()
    return continued_fraction.a_n, continued_fraction.b_n


def expected_pcf_coefficients() -> tuple[sp.Expr, sp.Expr]:
    """Return the printed challenge coefficients used as independent targets."""

    # ``a_n`` is the polynomial denominator term printed in the challenge.
    a_n = -(220 * n**3 + 484 * n**2 + 301 * n + 42)
    # ``b_n`` is the polynomial numerator term printed in the challenge.
    b_n = 4 * n**2 * (2 * n + 1) ** 2 * (5 * n - 4) * (5 * n + 6)
    return a_n, b_n


def deflation_factor() -> sp.Expr:
    """Recover the factor removed by the library's complete PCF deflation."""

    # The quotient of the raw and deflated a-coefficients is exactly c_n.
    factor = sp.cancel(raw_trajectory_pcf().a_n / challenge_pcf().a_n)
    return sp.factor(factor)


def raw_pcf_coefficients() -> tuple[sp.Expr, sp.Expr]:
    """Return coefficients produced by ``PCF(trajectory_matrix)`` before deflation."""

    # The raw PCF retains the polynomial factors later removed by deflate_all().
    continued_fraction = raw_trajectory_pcf()
    return continued_fraction.a_n, continued_fraction.b_n


def minimal_solution_scaling_ratio(index: sp.Expr = n) -> sp.Expr:
    """Derive ``s_n/s_(n-1)`` from the library PCF and companion recurrence."""

    # Since r_n A(n)=a_n, the ratio is recovered instead of transcribed.
    coefficient_a = companion_recurrence_coefficients()[0]
    compact_a = challenge_pcf().a_n
    ratio = sp.factor(sp.cancel(compact_a / coefficient_a))
    return ratio.subs({n: index})


@lru_cache
def hypergeometric_value(index: int) -> sp.Expr:
    """Evaluate ``F_index`` exactly with ``pFq.evaluate``.

    The library chooses an anchor hypergeometric state and transports it using
    its contiguous-relation CMF, so these values independently exercise the
    same built-in machinery used to construct the trajectory.
    """

    # ``parameter`` is the common pair of numerator parameters.
    parameter = sp.Rational(1, 2) + index
    # ``denominator_parameter`` advances three times as fast along the trajectory.
    denominator_parameter = sp.Rational(1, 2) + 3 * index
    return pFq.evaluate(
        [parameter, parameter],
        [denominator_parameter],
        HYPERGEOMETRIC_ARGUMENT,
    )


def hypergeometric_recurrence_point_checks(
    points: tuple[int, ...] = (1, 2, 3),
) -> dict[int, sp.Expr]:
    """Return exact recurrence residuals for independently expanded ``F_n``.

    At every requested regular integer ``k``, ``pFq.evaluate`` obtains the
    three exact hypergeometric values and the wrapper checks

    ``F_(k+2) - A(k) F_(k+1) - B(k) F_k = 0``.

    These point checks do not replace the contiguous-relation proof, but they
    independently guard the indexing and companion-matrix orientation.
    """

    # ``coefficient_a`` and ``coefficient_b`` are the derived rational recurrence data.
    coefficient_a, coefficient_b = companion_recurrence_coefficients()
    # ``residuals`` records one exact hypergeometric check at each selected index.
    residuals: dict[int, sp.Expr] = {}
    for point in points:
        value_0 = hypergeometric_value(point)
        value_1 = hypergeometric_value(point + 1)
        value_2 = hypergeometric_value(point + 2)
        residuals[point] = sp.simplify(
            value_2
            - coefficient_a.subs(n, point) * value_1
            - coefficient_b.subs(n, point) * value_0
        )
    return residuals


def euler_integral_components() -> dict[str, sp.Expr]:
    """Return the specialized Euler integrand and its ``h(t)^n psi(t)`` split.

    The mathematical proof cites Euler's formula.  This function verifies the
    specialization

    ``t^(n-1/2) (1-t)^(2n-1) (1-t/2)^(-n-1/2) = h(t)^n psi(t)``.
    """

    # ``t`` is the Euler-integration variable on the real interval [0, 1].
    t = sp.symbols("t", positive=True)
    # ``prefactor`` is the gamma quotient outside the Euler integral.
    prefactor = sp.gamma(3 * n + sp.Rational(1, 2)) / (
        sp.gamma(n + sp.Rational(1, 2)) * sp.gamma(2 * n)
    )
    # ``integrand`` is Euler's specialized integrand for the trajectory value F_n.
    integrand = (
        t ** (n - sp.Rational(1, 2))
        * (1 - t) ** (2 * n - 1)
        * (1 - t / 2) ** (-n - sp.Rational(1, 2))
    )
    # ``weight`` contains every factor raised to the large parameter n.
    weight = t * (1 - t) ** 2 / (1 - t / 2)
    # ``amplitude`` contains the remaining algebraic endpoint factors.
    amplitude = t ** (-sp.Rational(1, 2)) * (1 - t) ** -1 * (
        1 - t / 2
    ) ** (-sp.Rational(1, 2))
    return {
        "variable": t,
        "prefactor": prefactor,
        "integrand": integrand,
        "weight": weight,
        "amplitude": amplitude,
    }


def gamma_prefactor_ratio() -> sp.Expr:
    """Return the exact quotient ``P_(n+1)/P_n`` for the Euler prefactor.

    Gamma recurrence reduces the quotient to

    ``3(6n+1)(6n+5) / (8n(2n+1))``,

    whose limit is the exponential factor ``27/4`` used with the saddle.
    """

    # ``ratio`` follows by expanding the three numerator and three denominator factors.
    ratio = (
        (3 * n + sp.Rational(1, 2))
        * (3 * n + sp.Rational(3, 2))
        * (3 * n + sp.Rational(5, 2))
        / ((n + sp.Rational(1, 2)) * (2 * n) * (2 * n + 1))
    )
    return sp.factor(ratio)


def endpoint_bound_closed_form() -> sp.Expr:
    """Return the exact elementary upper bound for the Euler endpoint piece."""

    # ``bound`` equals 2^(n+1/2) times the integral of (1-t)^(2n-1) from 3/4 to 1.
    bound = 2 ** (n + sp.Rational(1, 2)) * sp.Rational(1, 4) ** (2 * n) / (
        2 * n
    )
    return sp.simplify(bound)


def exact_anchor_values() -> tuple[sp.Expr, sp.Expr]:
    """Compute the two Pincherle anchors using ``pFq.evaluate``."""

    # ``f_1`` is the first regular library-evaluated trajectory value.
    f_1 = hypergeometric_value(1)
    # ``f_2`` is the next library-evaluated value and determines the PCF tail.
    f_2 = hypergeometric_value(2)
    return f_1, f_2


def anchor_integral_certificates() -> dict[str, sp.Expr]:
    """Return exact rational-integral data proving the two anchor evaluations."""

    # ``u`` is the rationalizing variable u = tan(theta) after t = 2 sin(theta)^2.
    u = sp.symbols("u", real=True)
    # ``integrand_1`` is the rational integral remaining in the Euler integral for F_1.
    integrand_1 = u**2 * (1 - u**2) / (1 + u**2) ** 2
    # ``decomposition_1`` is a partial fraction certificate for the first integral.
    decomposition_1 = -1 + 3 / (1 + u**2) - 2 / (1 + u**2) ** 2
    # ``integrand_2`` is the rational integral remaining in the Euler integral for F_2.
    integrand_2 = u**4 * (1 - u**2) ** 3 / (1 + u**2) ** 4
    # ``decomposition_2`` is a partial fraction certificate for the second integral.
    decomposition_2 = (
        -u**2
        + 7
        - 25 / (1 + u**2)
        + 38 / (1 + u**2) ** 2
        - 28 / (1 + u**2) ** 3
        + 8 / (1 + u**2) ** 4
    )
    # ``value_1`` and ``value_2`` are the exact definite integrals on [0, 1].
    value_1 = (sp.pi - 3) / 2
    value_2 = 11 - 7 * sp.pi / 2
    return {
        "variable": u,
        "integrand_1": integrand_1,
        "decomposition_1": decomposition_1,
        "value_1": value_1,
        "integrand_2": integrand_2,
        "decomposition_2": decomposition_2,
        "value_2": value_2,
    }


def anchor_substitution_certificates() -> dict[str, sp.Expr]:
    """Return residuals for the rationalizing substitution in both anchors.

    With ``t = 2u^2/(1+u^2)``, the two Euler integrands including ``dt`` become
    ``4 sqrt(2) u^2(1-u^2)/(1+u^2)^2 du`` and
    ``8 sqrt(2) u^4(1-u^2)^3/(1+u^2)^4 du``.
    """

    # ``u`` is positive on the transformed integration interval [0, 1].
    u = sp.symbols("u", positive=True)
    # ``substitution`` combines t=2 sin(theta)^2 with u=tan(theta).
    substitution = 2 * u**2 / (1 + u**2)
    # ``jacobian`` is dt/du for the change of variables.
    jacobian = sp.diff(substitution, u)
    # ``residuals`` compares each transformed Euler integrand with its rational target.
    residuals: dict[str, sp.Expr] = {}
    for index, multiplier in ((1, 4 * sp.sqrt(2)), (2, 8 * sp.sqrt(2))):
        transformed = (
            substitution ** (index - sp.Rational(1, 2))
            * (1 - substitution) ** (2 * index - 1)
            * (1 - substitution / 2) ** (-index - sp.Rational(1, 2))
            * jacobian
        )
        target = (
            multiplier
            * u ** (2 * index)
            * (1 - u**2) ** (2 * index - 1)
            / (1 + u**2) ** (2 * index)
        )
        residuals[f"anchor_{index}"] = sp.simplify(transformed - target)
    return residuals


def anchor_basis_integrals() -> dict[int, sp.Expr]:
    """Return ``I_k = integral_0^1 (1+u^2)^(-k) du`` for ``k=1,...,4``.

    The values are generated from

    ``I_k = (2k-3)/(2k-2) I_(k-1) + 1/(2^k(k-1))``,

    exactly the integration-by-parts recurrence used in the anchor proof.
    """

    # ``values`` starts from the elementary arctangent integral I_1=pi/4.
    values: dict[int, sp.Expr] = {1: sp.pi / 4}
    for index in range(2, 5):
        recurrence_value = (
            sp.Rational(2 * index - 3, 2 * index - 2) * values[index - 1]
            + sp.Rational(1, 2**index * (index - 1))
        )
        values[index] = sp.simplify(recurrence_value)
    return values


def companion_characteristic_roots() -> tuple[sp.Expr, sp.Expr]:
    """Extract the two roots from the library-derived limiting matrix."""

    # ``roots`` comes from the exact eigenvalue calculation inherited by Matrix.
    roots = tuple(limiting_companion_matrix().eigenvals())
    # The Euler-selected root is positive; the dominant root is negative.
    small_root = next(root for root in roots if root.is_positive)
    dominant_root = next(root for root in roots if root.is_negative)
    return small_root, dominant_root


def limiting_companion_matrix() -> Matrix:
    """Return the entrywise limit of the exact companion matrix as n tends to infinity."""

    # ``companion_matrix`` was produced by Matrix.as_companion, not transcribed.
    companion_matrix = companion_matrix_113()
    return companion_matrix.applyfunc(lambda entry: sp.limit(entry, n, sp.oo))


def pcf_characteristic_roots() -> tuple[sp.Expr, sp.Expr]:
    """Derive factorial-balanced roots from the library-generated PCF coefficients."""

    # ``leading_a`` and ``leading_b`` are obtained from the compact PCF object.
    leading_a = sp.Poly(challenge_pcf().a_n, n).LC()
    leading_b = sp.Poly(challenge_pcf().b_n, n).LC()
    # For degree pattern (3,6), X_n~n!^3 lambda^n gives this balanced polynomial.
    root_variable = sp.symbols("lambda_pcf")
    roots = sp.solve(
        sp.Eq(root_variable**2 - leading_a * root_variable - leading_b, 0),
        root_variable,
    )
    # The compact recurrence has one positive small root and one negative root.
    small_root = next(root for root in roots if root.is_positive)
    dominant_root = next(root for root in roots if root.is_negative)
    return small_root, dominant_root


def saddle_point_data() -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Return the Euler-integral saddle, its weight, and the total small root."""

    # ``saddle`` is the unique interior maximizer of t(1-t)^2/(1-t/2).
    saddle = (3 - sp.sqrt(5)) / 2
    # ``integral_weight`` is the exponential contribution of the integral.
    integral_weight = -11 + 5 * sp.sqrt(5)
    # ``gamma_weight`` is the exponential contribution of the Gamma prefactor.
    gamma_weight = sp.Rational(27, 4)
    return saddle, integral_weight, sp.simplify(gamma_weight * integral_weight)


def saddle_point_certificate() -> dict[str, sp.Expr]:
    """Return exact data proving that the stated saddle is the unique interior maximum."""

    # ``components`` supplies the Euler weight h(t).
    components = euler_integral_components()
    # ``t`` and ``weight`` are kept together to avoid mismatched symbolic assumptions.
    t = components["variable"]
    weight = components["weight"]
    # ``saddle`` is the critical root lying strictly between zero and one.
    saddle = (3 - sp.sqrt(5)) / 2
    # ``other_root`` is the second quadratic critical root and lies beyond one.
    other_root = (3 + sp.sqrt(5)) / 2
    # ``derivative_target`` exposes all critical points and the harmless denominator.
    derivative_target = -4 * (t - 1) * (t**2 - 3 * t + 1) / (t - 2) ** 2
    return {
        "derivative_residual": sp.factor(sp.diff(weight, t) - derivative_target),
        "saddle": saddle,
        "other_root": other_root,
        "left_endpoint": sp.simplify(weight.subs(t, 0)),
        "right_endpoint": sp.simplify(weight.subs(t, 1)),
        "saddle_weight": sp.simplify(weight.subs(t, saddle)),
    }


def pcf_numerator_zeros() -> tuple[sp.Expr, ...]:
    """Return all exact zeros of the library-generated compact ``b_n``."""

    # Solving the already library-derived b_n avoids duplicating its factorization.
    return tuple(sp.solve(sp.Eq(challenge_pcf().b_n, 0), n))


def riccati_identity_residual() -> sp.Expr:
    """Verify the sign convention behind Pincherle's continued-fraction tail.

    For ``Z_n=a_n Z_(n-1)+b_n Z_(n-2)`` and
    ``R_n=-Z_n/Z_(n-1)``, the checked identity is
    ``R_(n-1)=b_n/(a_n+R_n)``.
    """

    # ``z_previous`` and ``z_previous_previous`` model two nonzero adjacent values.
    z_previous, z_previous_previous = sp.symbols(
        "z_previous z_previous_previous", nonzero=True
    )
    # ``a_symbol`` and ``b_symbol`` keep the calculation independent of this PCF.
    a_symbol, b_symbol = sp.symbols("a_symbol b_symbol")
    # ``z_current`` is supplied by the abstract second-order recurrence.
    z_current = a_symbol * z_previous + b_symbol * z_previous_previous
    # ``r_current`` and ``r_previous`` use the minus sign in the written proof.
    r_current = -z_current / z_previous
    r_previous = -z_previous / z_previous_previous
    return sp.cancel(r_previous - b_symbol / (a_symbol + r_current))


def transport_quotient_residual() -> sp.Expr:
    """Verify that common nonzero scaling preserves the minimality quotient."""

    # ``scale``, ``minimal_value``, and ``dominant_value`` represent one arbitrary index.
    scale, minimal_value, dominant_value = sp.symbols(
        "scale minimal_value dominant_value", nonzero=True
    )
    return sp.cancel(
        (scale * minimal_value) / (scale * dominant_value)
        - minimal_value / dominant_value
    )


def symbolic_tail() -> sp.Expr:
    """Return the exact Pincherle tail ``-X_0/X_(-1)``."""

    # ``f_1`` and ``f_2`` are the two exact hypergeometric anchor values.
    f_1, f_2 = exact_anchor_values()
    # ``r_0`` equals s_0/s_(-1), hence the tail is -r_0 F_2/F_1.
    r_0 = minimal_solution_scaling_ratio(0)
    return sp.simplify(-r_0 * f_2 / f_1)


def symbolic_limit() -> sp.Expr:
    """Evaluate the infinite PCF using the explicit minimal hypergeometric solution."""

    # ``a_0`` is the leading term outside the infinite continued-fraction tail.
    a_0 = pcf_coefficients()[0].subs(n, 0)
    return sp.simplify(a_0 + symbolic_tail())


def symbolic_verification() -> dict[str, bool]:
    """Check the exact identities and theorem hypotheses exposed by this verifier."""

    # ``trajectory_matrix`` and ``expected_trajectory`` test the five CMF basis steps.
    trajectory_matrix = trajectory_matrix_113()
    expected_trajectory = expected_trajectory_matrix_113()
    # ``conservation_valid`` is returned after the built-in pairwise CMF validation.
    conservation_valid = cmf_conservation_validation()
    # ``coboundary_matrix`` is discovered by the library's Krylov-basis construction.
    coboundary_matrix = companion_coboundary_matrix_113()
    # ``companion_matrix`` is generated by Matrix.as_companion.
    companion_matrix = companion_matrix_113()
    # ``expected_companion`` independently records the rational matrix in the proof.
    expected_companion = expected_companion_matrix_113()
    # ``coboundary_transform`` uses the library implementation of U^-1 T U(n+1).
    coboundary_transform = trajectory_matrix.coboundary(coboundary_matrix, n)
    # ``a_n`` and ``b_n`` come from PCF(trajectory).deflate_all().
    a_n, b_n = pcf_coefficients()
    # ``expected_a_n`` and ``expected_b_n`` are the printed challenge targets.
    expected_a_n, expected_b_n = expected_pcf_coefficients()
    # ``a_companion`` and ``b_companion`` are the two nontrivial companion entries.
    b_companion = companion_matrix[0, 1]
    a_companion = companion_matrix[1, 1]
    # ``r_n`` and ``r_previous`` encode the hypergeometric rescaling.
    r_n = minimal_solution_scaling_ratio()
    r_previous = minimal_solution_scaling_ratio(n - 1)
    # ``raw_a`` and ``raw_b`` check the exact normalization/deflation stage.
    raw_a, raw_b = raw_pcf_coefficients()
    # ``c_n`` is the factor removed by complete deflation.
    c_n = deflation_factor()
    # ``saddle``, ``integral_weight``, and ``combined_weight`` check the asymptotics.
    saddle, integral_weight, combined_weight = saddle_point_data()
    # ``euler_data`` exposes the exact integrand, exponential weight, and amplitude.
    euler_data = euler_integral_components()
    # ``integration_variable`` is shared by every expression in the Euler certificate.
    integration_variable = euler_data["variable"]
    # ``integrand_weight`` is the exponential base h(t) in Euler's integral.
    integrand_weight = euler_data["weight"]
    # ``saddle_certificate`` factors h'(t) and records both endpoints and critical roots.
    saddle_certificate = saddle_point_certificate()
    # ``gamma_ratio`` is the exact consecutive quotient of the gamma prefactor.
    gamma_ratio = gamma_prefactor_ratio()
    # ``f_1`` and ``f_2`` are independently evaluated by the library CMF.
    f_1, f_2 = exact_anchor_values()
    # ``expected_f_1`` and ``expected_f_2`` are the closed forms proved by integration.
    expected_f_1 = 15 * sp.sqrt(2) * (sp.pi - 3) / 2
    expected_f_2 = 1155 * sp.sqrt(2) * (22 - 7 * sp.pi) / 8
    # ``anchor_data`` certifies the elementary integrals used to evaluate F_1 and F_2.
    anchor_data = anchor_integral_certificates()
    # ``anchor_substitutions`` checks the rationalizing changes of variables.
    anchor_substitutions = anchor_substitution_certificates()
    # ``basis_integrals`` records I_1 through I_4 from the integration-by-parts recurrence.
    basis_integrals = anchor_basis_integrals()
    # ``u`` is the integration variable stored in the anchor certificate.
    u = anchor_data["variable"]
    # ``limiting_companion`` supplies the characteristic polynomial used by Poincare-Perron.
    limiting_companion = limiting_companion_matrix()
    # ``characteristic_variable`` is the spectral variable of the limiting matrix.
    characteristic_variable = sp.symbols("lambda")
    # ``characteristic_polynomial`` is det(lambda I - C_infinity).
    characteristic_polynomial = sp.factor(
        (characteristic_variable * Matrix.eye(2) - limiting_companion).det()
    )
    # ``small_root`` and ``dominant_root`` are the two claimed characteristic roots.
    small_root, dominant_root = companion_characteristic_roots()
    # ``pcf_small_root`` and ``pcf_dominant_root`` give the balanced PCF root pair.
    pcf_small_root, pcf_dominant_root = pcf_characteristic_roots()
    # ``hypergeometric_residuals`` independently test the recurrence at three indices.
    hypergeometric_residuals = hypergeometric_recurrence_point_checks()
    return {
        "cmf_conservation": conservation_valid,
        "trajectory_matrix": all(
            sp.cancel(entry) == 0
            for entry in (trajectory_matrix - expected_trajectory)
        ),
        "coboundary_basis_column": all(
            sp.cancel(entry) == 0 for entry in coboundary_basis_residual()
        ),
        "coboundary_identity": all(
            sp.cancel(entry) == 0
            for entry in (coboundary_transform - expected_companion)
        ),
        "companion_matrix": all(
            sp.cancel(entry) == 0
            for entry in (companion_matrix - expected_companion)
        ),
        "challenge_coefficient_a": sp.factor(a_n - expected_a_n) == 0,
        "challenge_coefficient_b": sp.factor(b_n - expected_b_n) == 0,
        "deflation_a": sp.factor(raw_a - c_n * a_n) == 0,
        "deflation_b": sp.factor(
            raw_b - c_n * c_n.subs(n, n - 1) * b_n
        )
        == 0,
        "minimal_solution_a": sp.cancel(a_n - r_n * a_companion) == 0,
        "minimal_solution_b": sp.cancel(
            b_n - r_n * r_previous * b_companion
        )
        == 0,
        "initial_scaling_ratio": sp.simplify(
            minimal_solution_scaling_ratio(0) - sp.Rational(24, 77)
        )
        == 0,
        "hypergeometric_recurrence_points": all(
            residual == 0 for residual in hypergeometric_residuals.values()
        ),
        "euler_integrand_factorization": sp.refine(
            sp.powsimp(
                euler_data["integrand"]
                / (euler_data["weight"] ** n * euler_data["amplitude"]),
                force=True,
            ),
            sp.Q.positive(1 - integration_variable),
        )
        == 1,
        "saddle_stationary": sp.simplify(
            sp.diff(integrand_weight, integration_variable).subs(
                integration_variable, saddle
            )
        )
        == 0,
        "saddle_weight": sp.simplify(
            integrand_weight.subs(integration_variable, saddle) - integral_weight
        )
        == 0,
        "saddle_derivative_factorization": (
            saddle_certificate["derivative_residual"] == 0
        ),
        "saddle_unique_interior_critical_point": (
            saddle_certificate["saddle"] > 0
            and saddle_certificate["saddle"] < 1
            and saddle_certificate["other_root"] > 1
        ),
        "saddle_endpoint_values": (
            saddle_certificate["left_endpoint"] == 0
            and saddle_certificate["right_endpoint"] == 0
            and saddle_certificate["saddle_weight"] > 0
        ),
        "gamma_prefactor_exponential_base": sp.limit(
            gamma_ratio, n, sp.oo
        )
        == sp.Rational(27, 4),
        "endpoint_bound_closed_form": sp.simplify(
            endpoint_bound_closed_form()
            - sp.sqrt(2) * sp.Rational(1, 8) ** n / (2 * n)
        )
        == 0,
        "small_root": sp.simplify(
            combined_weight - companion_characteristic_roots()[0]
        )
        == 0,
        "companion_limit": limiting_companion
        == Matrix([[0, sp.Rational(729, 4)], [1, -sp.Rational(297, 2)]]),
        "small_characteristic_root": sp.simplify(
            characteristic_polynomial.subs(characteristic_variable, small_root)
        )
        == 0,
        "dominant_characteristic_root": sp.simplify(
            characteristic_polynomial.subs(characteristic_variable, dominant_root)
        )
        == 0,
        "root_signs_and_distinct_moduli": (
            small_root > 0
            and dominant_root < 0
            and sp.Abs(dominant_root) > small_root
        ),
        "pcf_numerator_nonzero_for_positive_indices": set(pcf_numerator_zeros())
        == {
            -sp.Rational(6, 5),
            -sp.Rational(1, 2),
            sp.Integer(0),
            sp.Rational(4, 5),
        },
        "endpoint_base_below_saddle": sp.simplify(
            integral_weight - sp.Rational(1, 8)
        )
        > 0,
        "anchor_f1": sp.simplify(f_1 - expected_f_1) == 0,
        "anchor_f2": sp.simplify(f_2 - expected_f_2) == 0,
        "anchor_integrand_1_decomposition": sp.cancel(
            anchor_data["integrand_1"] - anchor_data["decomposition_1"]
        )
        == 0,
        "anchor_integrand_2_decomposition": sp.cancel(
            anchor_data["integrand_2"] - anchor_data["decomposition_2"]
        )
        == 0,
        "anchor_substitutions": all(
            residual == 0 for residual in anchor_substitutions.values()
        ),
        "anchor_basis_integrals": all(
            sp.simplify(
                sp.integrate((1 + u**2) ** (-index), (u, 0, 1))
                - value
            )
            == 0
            for index, value in basis_integrals.items()
        ),
        "anchor_integral_1": sp.simplify(
            sp.integrate(anchor_data["integrand_1"], (u, 0, 1))
            - anchor_data["value_1"]
        )
        == 0,
        "anchor_integral_2": sp.simplify(
            sp.integrate(anchor_data["integrand_2"], (u, 0, 1))
            - anchor_data["value_2"]
        )
        == 0,
        "transport_minimality_quotient": transport_quotient_residual() == 0,
        "pincherle_riccati_identity": riccati_identity_residual() == 0,
        "pincherle_tail": sp.simplify(
            symbolic_tail() - 6 * (22 - 7 * sp.pi) / (3 - sp.pi)
        )
        == 0,
        "leading_term": a_n.subs(n, 0) == -42,
        "closed_form_limit": sp.simplify(
            symbolic_limit() - 6 / (3 - sp.pi)
        )
        == 0,
        "root_ratio_invariant": sp.simplify(
            sp.Abs(dominant_root / small_root)
            - sp.Abs(pcf_dominant_root / pcf_small_root)
        )
        == 0,
    }


def coboundary_point_checks(points: tuple[int, ...] = (1, 2, 3, 4, 5)) -> int:
    """Verify the rational coboundary certificate at five regular indices."""

    # ``trajectory_matrix`` is the source CMF trajectory representation.
    trajectory_matrix = trajectory_matrix_113()
    # ``coboundary_matrix`` is the exact change of basis.
    coboundary_matrix = companion_coboundary_matrix_113()
    # ``companion_matrix`` is the independent paper target recurrence.
    companion_matrix = expected_companion_matrix_113()
    # ``transformed_matrix`` is computed by the library's coboundary method.
    transformed_matrix = trajectory_matrix.coboundary(coboundary_matrix, n)
    # ``matches`` counts independent substitutions satisfying the matrix identity.
    matches = 0
    for point in points:
        difference = (transformed_matrix - companion_matrix).subs({n: point})
        if all(sp.simplify(entry) == 0 for entry in difference):
            matches += 1
    return matches


def numerical_verification(depth: int = 300, dps: int = 500) -> NumericalVerification:
    """Evaluate the exact convergent and compare it with 6/(3-pi)."""

    # ``continued_fraction`` is the same library-derived and deflated PCF used above.
    continued_fraction = challenge_pcf()
    # ``started_at`` measures the realistic wall-clock cost of the requested depth.
    started_at = time.perf_counter()
    with mp.workdps(dps):
        # ``convergent`` is retained as an exact rational before conversion to mpmath.
        convergent = continued_fraction.limit(depth)
        # ``value`` avoids binary-float truncation by converting numerator and denominator separately.
        value = mp.mpf(int(convergent.p())) / mp.mpf(int(convergent.q()))
        # ``target`` is evaluated at the same arbitrary precision.
        target = 6 / (3 - mp.pi)
        # ``absolute_error`` measures the independently computed numerical discrepancy.
        absolute_error = mp.fabs(value - target)
        # ``digits`` counts correct decimal digits conservatively from the absolute error.
        digits = int(mp.floor(-mp.log10(absolute_error)))
    # ``elapsed_seconds`` reports the complete exact-evaluation and comparison time.
    elapsed_seconds = time.perf_counter() - started_at
    return NumericalVerification(
        depth=depth,
        digits=digits,
        absolute_error=absolute_error,
        elapsed_seconds=elapsed_seconds,
        value=value,
        target=target,
    )


def main() -> None:
    """Run the symbolic certificate, multi-point check, and numerical validation."""

    # ``checks`` contains one Boolean result for every exact identity in the proof.
    checks = symbolic_verification()
    # ``point_matches`` implements the required independent five-point matrix check.
    point_matches = coboundary_point_checks()
    # ``numeric`` supplies a 500-digit cross-check at depth 300.
    numeric = numerical_verification()
    for check_name, passed in checks.items():
        print(f"{check_name}: {'PASS' if passed else 'FAIL'}")
    print(f"coboundary multi-point check: {point_matches}/5 MATCH")
    print(f"depth: {numeric.depth}")
    print(f"correct digits: {numeric.digits}")
    print(f"absolute error: {mp.nstr(numeric.absolute_error, 12)}")
    print(f"elapsed seconds: {numeric.elapsed_seconds:.6f}")
    if not all(checks.values()) or point_matches != 5:
        raise SystemExit("At least one exact derivation check failed.")


if __name__ == "__main__":
    main()
